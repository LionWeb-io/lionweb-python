from enum import Enum
from typing import Callable, List, Optional, TypedDict, cast

from lionweb import LionWebVersion

from .annotation import Annotation
from .classifier import Classifier
from .concept import Concept
from .data_type import DataType
from .enumeration import Enumeration
from .enumeration_literal import EnumerationLiteral
from .interface import Interface
from .language import Language
from .primitive_type import PrimitiveType
from .property import Property
from .reference import Reference


class Multiplicity(Enum):
    OPTIONAL = {"required": False, "many": False}
    REQUIRED = {"required": True, "many": False}
    ZERO_OR_MORE = {"required": False, "many": True}
    ONE_OR_MORE = {"required": True, "many": True}


class PropertyData(TypedDict):
    name: str
    type: "PrimitiveTypeFactory | EnumerationTypeFactory | DataType"
    multiplicity: Multiplicity
    id: Optional[str]
    key: Optional[str]


class ReferenceData(TypedDict):
    name: str
    type: "ClassifierFactory"
    multiplicity: Multiplicity
    id: Optional[str]
    key: Optional[str]


class ClassifierFactory:

    def __init__(
        self,
        type: str,
        name: str,
        id: str,
        key: str,
        extends: List["ClassifierFactory | Classifier"] = [],
    ):
        self.type = type
        self.name = name
        self.abstract = False
        self.partition = False
        self.id = id
        self.key = key
        self.properties: List[PropertyData] = []
        self.references: List[ReferenceData] = []
        self.annotates: Optional[Classifier | ClassifierFactory] = None
        self.extends = extends

    def property(
        self,
        name: str,
        type: "PrimitiveTypeFactory | EnumerationTypeFactory | DataType",
        multiplicity: Multiplicity = Multiplicity.REQUIRED,
        id: Optional[str] = None,
        key: Optional[str] = None,
    ) -> "ClassifierFactory":
        self.properties.append(
            {
                "name": name,
                "type": type,
                "multiplicity": multiplicity,
                "id": id,
                "key": key,
            }
        )
        return self

    def reference(
        self,
        name: str,
        type: "ClassifierFactory",
        multiplicity: Multiplicity = Multiplicity.REQUIRED,
        id: Optional[str] = None,
        key: Optional[str] = None,
    ) -> "ClassifierFactory":
        self.references.append(
            {
                "name": name,
                "type": type,
                "multiplicity": multiplicity,
                "id": id,
                "key": key,
            }
        )
        return self

    def populate(
        self,
        classifier: Classifier,
        id_calculator: Callable[[Optional[str], str], str],
        key_calculator: Callable[[Optional[str], str], str],
    ):
        language = classifier.language
        assert language is not None
        for property_data in self.properties:
            property = Property(
                lion_web_version=classifier.lion_web_version,
                name=property_data.get("name"),
                container=classifier,
                id=property_data["id"]
                or id_calculator(classifier.id, property_data["name"]),
                key=property_data["key"]
                or key_calculator(classifier.key, property_data["name"]),
            )
            property.set_optional(not property_data["multiplicity"].value["required"])
            property_type = property_data["type"]
            if isinstance(property_type, DataType):
                type = property_type
            else:
                if isinstance(property_type, PrimitiveTypeFactory):
                    type_name = property_type.name
                elif isinstance(property_type, EnumerationTypeFactory):
                    type_name = property_type.name
                type = language.require_data_type_by_name(type_name)
                if type is None:
                    raise ValueError(f"Type {type_name} not found")
            property.type = type
            classifier.add_feature(property)
        for ref_data in self.references:
            reference = Reference(
                lion_web_version=classifier.lion_web_version,
                name=ref_data["name"],
                container=classifier,
                id=ref_data["id"] or id_calculator(classifier.id, ref_data["name"]),
                key=ref_data["key"] or key_calculator(classifier.key, ref_data["name"]),
            )
            reference.set_optional(not ref_data["multiplicity"].value["required"])
            reference.set_multiple(ref_data["multiplicity"].value["many"])
            type_name = ref_data["type"].name
            link_type = language.require_classifier_by_name(type_name)
            if link_type is None:
                raise ValueError(f"Type {type_name} not found")
            reference.set_type(link_type)
            classifier.add_feature(reference)
        if isinstance(classifier, Annotation):
            if isinstance(self.annotates, ClassifierFactory):
                classifier.annotates = language.require_classifier_by_name(
                    self.annotates.name
                )
            elif isinstance(self.annotates, Classifier):
                classifier.annotates = self.annotates
        elif isinstance(classifier, Interface):
            for extends in self.extends:
                if isinstance(extends, ClassifierFactory):
                    classifier.add_extended_interface(
                        language.require_interface_by_name(extends.name)
                    )
                elif isinstance(extends, Classifier):
                    classifier.add_extended_interface(cast(Interface, extends))

    def build(self, language: Language) -> "Classifier":
        if self.type == "Concept":
            concept = Concept(
                lion_web_version=language.lion_web_version,
                language=language,
                abstract=self.abstract,
                partition=self.partition,
                id=self.id,
                key=self.key,
                name=self.name,
            )
            return concept
        elif self.type == "Interface":
            interface = Interface(
                lion_web_version=language.lion_web_version,
                language=language,
                id=self.id,
                key=self.key,
                name=self.name,
            )
            return interface
        elif self.type == "Annotation":
            annotation = Annotation(
                lion_web_version=language.lion_web_version,
                language=language,
                id=self.id,
                key=self.key,
                name=self.name,
            )
            return annotation
        else:
            raise ValueError(f"Invalid classifier type: {self.type}")

    def set_annotates(self, annotates: "Classifier | ClassifierFactory"):
        self.annotates = annotates


class PrimitiveTypeFactory:

    def __init__(self, name: str, id: str, key: str):
        self.name = name
        self.id = id
        self.key = key

    def build(self, language: Language) -> "PrimitiveType":
        ptype = PrimitiveType(
            lion_web_version=language.lion_web_version,
            language=language,
            name=self.name,
            id=self.id,
            key=self.key,
        )
        return ptype


class EnumerationTypeFactory:

    def __init__(self, name: str, id: str, key: str, literals: List[str]):
        self.name = name
        self.id = id
        self.key = key
        self.literals = literals

    def build(
        self,
        language: Language,
        id_calculator: Callable[[Optional[str], str], str],
        key_calculator: Callable[[Optional[str], str], str],
    ) -> "Enumeration":
        enumeration = Enumeration(
            lion_web_version=language.lion_web_version,
            language=language,
            name=self.name,
            id=self.id,
            key=self.key,
        )
        for literal_name in self.literals:
            literal = EnumerationLiteral(
                lion_web_version=language.lion_web_version,
                enumeration=enumeration,
                name=literal_name,
            )
            literal.set_id(id_calculator(enumeration.id, literal_name))
            literal.set_key(key_calculator(enumeration.key, literal_name))
        return enumeration


class LanguageFactory:

    def __init__(
        self,
        name: str,
        lw_version: Optional[LionWebVersion] = None,
        version: str = "1",
        id: Optional[str] = None,
        key: Optional[str] = None,
        id_calculator: Optional[Callable[[Optional[str], str], str]] = None,
        key_calculator: Optional[Callable[[Optional[str], str], str]] = None,
    ):
        self.lw_version = lw_version or LionWebVersion.current_version()
        self.version = version
        self.name = name
        self.id_calculator = id_calculator or (
            lambda parent_id, name: name if parent_id is None else f"{parent_id}_{name}"
        )
        self.key_calculator = key_calculator or (
            lambda parent_key, name: (
                name if parent_key is None else f"{parent_key}_{name}"
            )
        )
        self.id = id or self.id_calculator(None, name)
        self.key = key or self.key_calculator(None, name)
        self.classifiers: List[ClassifierFactory] = []
        self.primitive_types: List[PrimitiveTypeFactory] = []
        self.enumerations: List[EnumerationTypeFactory] = []

    def build(self) -> Language:
        language = Language(
            name=self.name,
            id=self.id,
            key=self.key,
            version=self.version,
            lion_web_version=self.lw_version,
        )

        for primitive_type in self.primitive_types:
            primitive_type.build(language)
        for enumeration in self.enumerations:
            enumeration.build(language, self.id_calculator, self.key_calculator)

        classifiers = {}
        for classifier in self.classifiers:
            classifiers[classifier] = classifier.build(language)
        for classifier in self.classifiers:
            classifier.populate(
                classifiers[classifier], self.id_calculator, self.key_calculator
            )

        return language

    def concept(
        self, name: str, id: Optional[str] = None, key: Optional[str] = None
    ) -> ClassifierFactory:
        sub = ClassifierFactory(
            "Concept",
            name,
            id=id or self.id_calculator(self.id, name),
            key=key or self.key_calculator(self.key, name),
        )
        self.classifiers.append(sub)
        return sub

    def interface(
        self,
        name: str,
        id: Optional[str] = None,
        key: Optional[str] = None,
        extends: List[ClassifierFactory | Classifier] = [],
    ) -> ClassifierFactory:
        sub = ClassifierFactory(
            "Interface",
            name,
            id=id or self.id_calculator(self.id, name),
            key=key or self.key_calculator(self.key, name),
            extends=extends,
        )
        self.classifiers.append(sub)
        return sub

    def annotation(
        self,
        name: str,
        annotates: ClassifierFactory | Classifier,
        id: Optional[str] = None,
        key: Optional[str] = None,
    ) -> ClassifierFactory:
        sub = ClassifierFactory(
            "Annotation",
            name,
            id=id or self.id_calculator(self.id, name),
            key=key or self.key_calculator(self.key, name),
        )
        sub.set_annotates(annotates)
        self.classifiers.append(sub)
        return sub

    def primitive_type(
        self, name: str, id: Optional[str] = None, key: Optional[str] = None
    ) -> PrimitiveTypeFactory:
        sub = PrimitiveTypeFactory(
            name,
            id=id or self.id_calculator(self.id, name),
            key=key or self.key_calculator(self.key, name),
        )
        self.primitive_types.append(sub)
        return sub

    def enumeration(
        self,
        name: str,
        literals: List[str],
        id: Optional[str] = None,
        key: Optional[str] = None,
    ) -> EnumerationTypeFactory:
        sub = EnumerationTypeFactory(
            name,
            id=id or self.id_calculator(self.id, name),
            key=key or self.key_calculator(self.key, name),
            literals=literals,
        )
        self.enumerations.append(sub)
        return sub
