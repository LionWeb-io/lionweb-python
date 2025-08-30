from enum import Enum
from typing import Callable, Optional

from lionweb.language import Concept

from lionweb import LionWebVersion

from .language import Language

class Multiplicity(Enum):
    OPTIONAL = (False, False)
    REQUIRED = (True, False),
    ZERO_OR_MORE = (False, True),
    ONE_OR_MORE = (True, True)

class PropertyFactory:
    pass

class ClassifierFactory:

    def __init__(self, type: str, name: str):
        self.type = type
        self.name = name
        self.abstract = False
        self.partition = False

    def property(self, name: str, type: 'PrimitiveTypeFactory', multiplity: Multiplicity = Multiplicity.REQUIRED) -> 'ClassifierFactory':
        return self

    def reference(self, name: str, type: 'PrimitiveTypeFactory', multiplity: Multiplicity = Multiplicity.REQUIRED) -> 'ClassifierFactory':
        return self

    def build(self, language: Language) -> "Classifier":
        if self.type == "Concept":
            concept = Concept(lion_web_version=language.lion_web_version,
                              language=language,
                              abstract=self.abstract,
                              partition=self.partition,
                              name=self.name)
            return concept
        else:
            raise ValueError(f"Invalid classifier type: {self.type}")

class PrimitiveTypeFactory:

    def build(self) -> "PrimitiveType":
        pass


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
        self.key = key or key_calculator(None, key)
        self.classifiers = []
        self.primitive_types = []

    def build(self) -> Language:
        language = Language(name=self.name, id=self.id, key=self.key, version=self.version, lion_web_version=self.lw_version)

        for classifier in self.classifiers:
            classifier.build(language)

        for primitive_type in self.primitive_types:
            primitive_type.build()

        return language

    def concept(self, name: str) -> ClassifierFactory:
        sub = ClassifierFactory('Concept', name)
        self.classifiers.append(sub)
        return sub

    def interface(self, name: str) -> ClassifierFactory:
        pass

    def primitive_type(self, name: str) -> PrimitiveTypeFactory:
        pass

