from enum import Enum
from typing import Callable, Optional

from lionweb.language import Concept, PrimitiveType, Property, Reference, Classifier

from lionweb import LionWebVersion

from .language import Language

class Multiplicity(Enum):
    OPTIONAL = {'required':False, 'many':False }
    REQUIRED = {'required':True, 'many':False}
    ZERO_OR_MORE = {'required':False, 'many':True}
    ONE_OR_MORE = {'required':True, 'many':True}

class ClassifierFactory:

    def __init__(self, type: str, name: str, id: str, key: str):
        self.type = type
        self.name = name
        self.abstract = False
        self.partition = False
        self.id = id
        self.key = key
        self.properties = []
        self.references = []

    def property(self, name: str, type: 'PrimitiveTypeFactory',
                 multiplicity: Multiplicity = Multiplicity.REQUIRED,
                 id: Optional[str] = None, key: Optional[str] = None) -> 'ClassifierFactory':
        self.properties.append({
            "name": name,
            "type": type,
            'multiplicity': multiplicity,
            'id': id,
            'key': key
        })
        return self

    def reference(self, name: str, type: 'ClassifierFactory',
                  multiplicity: Multiplicity = Multiplicity.REQUIRED,
                  id: Optional[str] = None, key: Optional[str] = None) -> 'ClassifierFactory':
        self.references.append({
            "name": name,
            "type": type,
            'multiplicity': multiplicity,
            'id': id,
            'key': key
        })
        return self

    def populate(self, classifier: Classifier, id_calculator: Optional[Callable[[Optional[str], str], str]],
                 key_calculator: Optional[Callable[[Optional[str], str], str]]):
        language = classifier.language
        for property_data in self.properties:
            property = Property(lion_web_version=classifier.lion_web_version,
                                name = property_data.get("name"),
                                container = classifier,
                                id=property_data.get("id") or id_calculator(classifier.id, property_data.get("name")),
                                key=property_data.get("key") or key_calculator(classifier.key, property_data.get("name")))
            property.set_optional(not property_data.get("multiplicity").value['required'])
            type_name = property_data.get("type").name
            type = language.get_primitive_type_by_name(type_name)
            if type is None:
                raise ValueError(f"Type {type_name} not found")
            property.type = type
            classifier.add_feature(property)
        for ref_data in self.references:
            reference = Reference(lion_web_version=classifier.lion_web_version,
                                  name = ref_data.get("name"),
                                  container = classifier,
                                  id=ref_data.get("id") or id_calculator(classifier.id, ref_data.get("name")),
                                  key=ref_data.get("key") or key_calculator(classifier.key, ref_data.get("name")))
            reference.set_optional(not ref_data.get("multiplicity").value['required'])
            reference.set_multiple(ref_data.get("multiplicity").value['many'])
            type_name = ref_data.get("type").name
            type = language.get_classifier_by_name(type_name)
            if type is None:
                raise ValueError(f"Type {type_name} not found")
            reference.type = type
            classifier.add_feature(reference)

    def build(self, language: Language) -> "Classifier":
        if self.type == "Concept":
            concept = Concept(lion_web_version=language.lion_web_version,
                              language=language,
                              abstract=self.abstract,
                              partition=self.partition,
                              id=self.id,
                              key=self.key,
                              name=self.name)
            return concept
        else:
            raise ValueError(f"Invalid classifier type: {self.type}")

class PrimitiveTypeFactory:

    def __init__(self, name: str, id: str, key: str):
        self.name = name
        self.id = id
        self.key = key

    def build(self, language: Language) -> "PrimitiveType":
        ptype = PrimitiveType(lion_web_version=language.lion_web_version,
                          language=language,
                          name=self.name)
        return ptype


class LanguageFactory:

    def __init__(self, name: str,
                 lw_version: Optional[LionWebVersion] = None,
                 version: str = "1",
                 id: Optional[str] = None,
                 key: Optional[str] = None,
                 id_calculator: Optional[Callable[[Optional[str], str], str]] = None,
                 key_calculator: Optional[Callable[[Optional[str], str], str]] = None):
        self.lw_version = lw_version or LionWebVersion.current_version()
        self.version = version
        self.name = name
        self.id_calculator = id_calculator or (lambda parent_id, name: name if parent_id is None else f"{parent_id}_{name}")
        self.key_calculator = key_calculator or (lambda parent_key, name: name if parent_key is None else f"{parent_key}_{name}")
        self.id = id or id_calculator(None, name)
        self.key = key or key_calculator(None, name)
        self.classifiers = []
        self.primitive_types = []

    def build(self) -> Language:
        language = Language(name=self.name, id=self.id, key=self.key, version=self.version, lion_web_version=self.lw_version)

        for primitive_type in self.primitive_types:
            primitive_type.build(language)

        classifiers = {}
        for classifier in self.classifiers:
            classifiers[classifier] = classifier.build(language)
        for classifier in self.classifiers:
            classifier.populate(classifiers[classifier], self.id_calculator, self.key_calculator)

        return language

    def concept(self, name: str, id: Optional[str] = None, key: Optional[str] = None) -> ClassifierFactory:
        sub = ClassifierFactory('Concept', name,
                                id=id or self.id_calculator(self.id, name),
                                key=key or self.key_calculator(self.key, name))
        self.classifiers.append(sub)
        return sub

    def interface(self, name: str) -> ClassifierFactory:
        pass

    def primitive_type(self, name: str, id: Optional[str] = None, key: Optional[str] = None) -> PrimitiveTypeFactory:
        sub = PrimitiveTypeFactory(name,
                                id=id or self.id_calculator(self.id, name),
                                key=key or self.key_calculator(self.id, name))
        self.primitive_types.append(sub)
        return sub

