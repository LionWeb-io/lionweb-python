from collections.abc import Callable
from enum import Enum
from typing import TypedDict, cast

from lionweb import LionWebVersion

from .annotation import Annotation
from .classifier import Classifier
from .concept import Concept
from .containment import Containment
from .data_type import DataType
from .enumeration import Enumeration
from .enumeration_literal import EnumerationLiteral
from .interface import Interface
from .language import Language
from .language_entity import LanguageEntity
from .link import Link
from .primitive_type import PrimitiveType
from .property import Property
from .reference import Reference


class Multiplicity(Enum):
    """
    Defines an enumeration for Multiplicity levels.

    This enumeration is used to represent various levels of multiplicity for features.
    It provides four standard levels:
    OPTIONAL, REQUIRED, ZERO_OR_MORE, and ONE_OR_MORE.
    """

    OPTIONAL = {"required": False, "many": False}
    REQUIRED = {"required": True, "many": False}
    ZERO_OR_MORE = {"required": False, "many": True}
    ONE_OR_MORE = {"required": True, "many": True}


class PropertyData(TypedDict):
    """
    Represents a dictionary-based structure for defining property metadata.

    Attributes:
        name: The name of the property. Must be a string.
        type: The data type of the property. Accepts either a primitive type
              factory, an enumeration type factory, or an already existing data type.
        multiplicity: Specifies the multiplicity of the property (e.g., whether
                      it is single-valued or multi-valued).
        id: Optional field for an identifier for the property. If provided, must
            be a string.
        key: Optional field for a key that may be used to uniquely identify the
             property in a composite structure. If provided, must be a string.
    """

    name: str
    type: "PrimitiveTypeFactory | EnumerationTypeFactory | DataType"
    multiplicity: Multiplicity
    id: str | None
    key: str | None


class LinkData(TypedDict):
    name: str
    type: "ClassifierFactory | Classifier"
    multiplicity: Multiplicity
    id: str | None
    key: str | None


class LiteralData(TypedDict):
    name: str
    id: str | None
    key: str | None


# The class of each feature declared in a ClassifierFactory
FeatureClass = type[Property] | type[Reference] | type[Containment]


class ClassifierFactory:
    """
    A factory class for creating and managing different types of classifiers.

    This class provides mechanisms for defining classifiers, including their properties,
    references, and containments. It enables streamlined construction of models
    and metadata through a fluent interface. The supported classifier types include
    Concept, Interface, and Annotation. The factory ensures proper linking between
    classifiers and their features, leveraging optional and multiple configurations for
    flexibility. Features are created in the order in which they are declared.

    Types, extended and implemented classifiers can be factories of the same
    LanguageFactory or already built elements, including elements of other languages.

    Attributes:
        type: The type of the classifier (one of "Concept", "Interface", "Annotation").
        name: The name of the classifier.
        id: A unique identifier for the classifier.
        key: A unique key for identifying the classifier.
        extends: The classifiers this classifier extends: the extended interfaces of an
            Interface, or at most one extended Concept or Annotation.
        implements: The interfaces implemented by a Concept or an Annotation.
        abstract: Whether a Concept is abstract.
        partition: Whether a Concept is a partition.
    """

    def __init__(
        self,
        type: str,
        name: str,
        id: str,
        key: str,
        extends: list["ClassifierFactory | Classifier"] | None = None,
        implements: list["ClassifierFactory | Interface"] | None = None,
        abstract: bool = False,
        partition: bool = False,
    ):
        self.type = type
        self.name = name
        self.abstract = abstract
        self.partition = partition
        self.id = id
        self.key = key
        self.features: list[tuple[FeatureClass, PropertyData | LinkData]] = []
        self.annotates: Classifier | ClassifierFactory | None = None
        self.extends: list[ClassifierFactory | Classifier] = list(extends or [])
        self.implements: list[ClassifierFactory | Interface] = list(implements or [])

    def property(
        self,
        name: str,
        type: "PrimitiveTypeFactory | EnumerationTypeFactory | DataType",
        multiplicity: Multiplicity = Multiplicity.REQUIRED,
        id: str | None = None,
        key: str | None = None,
    ) -> "ClassifierFactory":
        self.features.append(
            (
                Property,
                {
                    "name": name,
                    "type": type,
                    "multiplicity": multiplicity,
                    "id": id,
                    "key": key,
                },
            )
        )
        return self

    def reference(
        self,
        name: str,
        type: "ClassifierFactory | Classifier",
        multiplicity: Multiplicity = Multiplicity.REQUIRED,
        id: str | None = None,
        key: str | None = None,
    ) -> "ClassifierFactory":
        self.features.append(
            (
                Reference,
                {
                    "name": name,
                    "type": type,
                    "multiplicity": multiplicity,
                    "id": id,
                    "key": key,
                },
            )
        )
        return self

    def containment(
        self,
        name: str,
        type: "ClassifierFactory | Classifier",
        multiplicity: Multiplicity = Multiplicity.REQUIRED,
        id: str | None = None,
        key: str | None = None,
    ) -> "ClassifierFactory":
        self.features.append(
            (
                Containment,
                {
                    "name": name,
                    "type": type,
                    "multiplicity": multiplicity,
                    "id": id,
                    "key": key,
                },
            )
        )
        return self

    def populate(
        self,
        classifier: Classifier,
        id_calculator: Callable[[str | None, str], str],
        key_calculator: Callable[[str | None, str], str],
        built: "dict[EntityFactory, LanguageEntity]",
    ):
        """Add the features and the relations to other classifiers to `classifier`.

        Args:
            classifier: The classifier built from this factory.
            id_calculator: Calculates the id of features without an explicit one.
            key_calculator: Calculates the key of features without an explicit one.
            built: The elements built so far, by the factory that defined them.
        """
        for feature_class, data in self.features:
            feature = feature_class(
                lion_web_version=classifier.lion_web_version,
                name=data["name"],
                container=classifier,
                id=data["id"] or id_calculator(classifier.id, data["name"]),
                key=data["key"] or key_calculator(classifier.key, data["name"]),
            )
            feature.set_optional(not data["multiplicity"].value["required"])
            feature_type = _resolve(data["type"], built)
            if isinstance(feature, Link):
                feature.set_multiple(data["multiplicity"].value["many"])
                feature.set_type(cast(Classifier, feature_type))
            else:
                feature.type = cast(DataType, feature_type)
            classifier.add_feature(feature)
        if isinstance(classifier, Concept):
            if len(self.extends) > 1:
                raise ValueError(f"Concept {self.name} can extend at most one concept")
            for extended in self.extends:
                classifier.set_extended_concept(cast(Concept, _resolve(extended, built)))
            for implemented in self.implements:
                classifier.add_implemented_interface(cast(Interface, _resolve(implemented, built)))
        elif isinstance(classifier, Annotation):
            if self.annotates is not None:
                classifier.annotates = cast(Classifier, _resolve(self.annotates, built))
            if len(self.extends) > 1:
                raise ValueError(f"Annotation {self.name} can extend at most one annotation")
            for extended in self.extends:
                classifier.extended_annotation = cast(Annotation, _resolve(extended, built))
            for implemented in self.implements:
                classifier.add_implemented_interface(cast(Interface, _resolve(implemented, built)))
        elif isinstance(classifier, Interface):
            for extended in self.extends:
                classifier.add_extended_interface(cast(Interface, _resolve(extended, built)))

    def build(self, language: Language) -> "Classifier":
        match self.type:
            case "Concept":
                return Concept(
                    lion_web_version=language.lion_web_version,
                    language=language,
                    abstract=self.abstract,
                    partition=self.partition,
                    id=self.id,
                    key=self.key,
                    name=self.name,
                )
            case "Interface":
                return Interface(
                    lion_web_version=language.lion_web_version,
                    language=language,
                    id=self.id,
                    key=self.key,
                    name=self.name,
                )
            case "Annotation":
                return Annotation(
                    lion_web_version=language.lion_web_version,
                    language=language,
                    id=self.id,
                    key=self.key,
                    name=self.name,
                )
            case _:
                raise ValueError(f"Invalid classifier type: {self.type}")

    def set_extends(self, extends: "Classifier | ClassifierFactory") -> "ClassifierFactory":
        self.extends = [extends]
        return self

    def set_annotates(self, annotates: "Classifier | ClassifierFactory") -> "ClassifierFactory":
        self.annotates = annotates
        return self


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
    def __init__(self, name: str, id: str, key: str, literals: list[str | LiteralData]):
        self.name = name
        self.id = id
        self.key = key
        self.literals = literals

    def build(
        self,
        language: Language,
        id_calculator: Callable[[str | None, str], str],
        key_calculator: Callable[[str | None, str], str],
    ) -> "Enumeration":
        enumeration = Enumeration(
            lion_web_version=language.lion_web_version,
            language=language,
            name=self.name,
            id=self.id,
            key=self.key,
        )
        for literal_data in self.literals:
            if isinstance(literal_data, str):
                literal = EnumerationLiteral(
                    lion_web_version=language.lion_web_version,
                    enumeration=enumeration,
                    name=literal_data,
                )
                literal.set_id(id_calculator(enumeration.id, literal_data))
                literal.set_key(key_calculator(enumeration.key, literal_data))
            else:
                literal = EnumerationLiteral(
                    lion_web_version=language.lion_web_version,
                    enumeration=enumeration,
                    name=literal_data["name"],
                )
                literal.set_id(
                    literal_data.get("id") or id_calculator(enumeration.id, literal_data["name"])
                )
                literal.set_key(
                    literal_data.get("key") or key_calculator(enumeration.key, literal_data["name"])
                )
        return enumeration


EntityFactory = ClassifierFactory | PrimitiveTypeFactory | EnumerationTypeFactory


def _resolve(
    element: "EntityFactory | LanguageEntity", built: "dict[EntityFactory, LanguageEntity]"
) -> LanguageEntity:
    """Return the element built from a factory, or the element itself if already built."""
    if isinstance(element, ClassifierFactory | PrimitiveTypeFactory | EnumerationTypeFactory):
        if element not in built:
            raise ValueError(
                f"{element.name} is defined by another LanguageFactory: "
                "use the element built by that factory instead"
            )
        return built[element]
    return element


class LanguageFactory:
    """
    Represents a factory for creating and managing languages and their components.

    This class provides a way to construct various elements of a language such as concepts,
    interfaces, annotations, primitive types, and enumerations. It allows defining a structured
    language model and handles the assignment of identifiers and keys for each component.

    Attributes:
        lw_version: The LionWebVersion of the language.
        version: Version number of the language as a string.
        name: The name of the language.
        id_calculator: A function to calculate the ID for language components.
        key_calculator: A function to calculate the key for language components.
        id: The identifier for the language.
        key: The key for the language.
        classifiers: List of ClassifierFactory objects included in the language.
        primitive_types: List of PrimitiveTypeFactory objects representing primitive types in the language.
        enumerations: List of EnumerationTypeFactory objects representing enumerations in the language.

    Methods:
        build:
            Generates a Language instance by assembling all language components.
        concept:
            Creates a new concept classifier and adds it to the language.
        interface:
            Creates a new interface classifier and adds it to the language.
        annotation:
            Creates a new annotation classifier and associates it with a specified element.
        primitive_type:
            Creates a new primitive type and adds it to the language.
        enumeration:
            Creates a new enumeration type and adds it to the language.
    """

    def __init__(
        self,
        name: str,
        lw_version: LionWebVersion | None = None,
        version: str = "1",
        id: str | None = None,
        key: str | None = None,
        id_calculator: Callable[[str | None, str], str] | None = None,
        key_calculator: Callable[[str | None, str], str] | None = None,
        dependencies: list[Language] | None = None,
    ):
        """
        Initializes a new instance of the class with provided parameters and default values where
        applicable. This constructor sets up foundational attributes for the instance, including name,
        version, identifier, and calculators for generating IDs and keys. Attributes related to
        classifiers, primitive types, and enumerations are also initialized as empty lists.

        Parameters:
            name (str): The name for the instance.
            lw_version (Optional[LionWebVersion]): The version of the LionWeb. Defaults to None,
                in which case the current version is used.
            version (str): The version of the instance. Default is "1".
            id (Optional[str]): The identifier for the instance. Defaults to None, in which case
                a default ID is calculated.
            key (Optional[str]): The key of the instance. Defaults to None, in which case a
                default key is calculated.
            id_calculator (Optional[Callable[[Optional[str], str], str]]): A function to calculate
                the instance ID. Defaults to a lambda function to generate ID based on parent ID
                and name if not provided.
            key_calculator (Optional[Callable[[Optional[str], str], str]]): A function to calculate
                the instance key. Defaults to a lambda function to generate key based on parent key
                and name if not provided.
            dependencies (Optional[list[Language]]): The languages this language depends on.

        Attributes:
            lw_version (LionWebVersion): The LionWeb version associated with the instance.
            version (str): The version of the instance.
            name (str): The name of the instance.
            id (str): The identifier of the instance.
            key (str): The key of the instance.
            classifiers (List[ClassifierFactory]): List to store classifier factories related
                to the instance.
            primitive_types (List[PrimitiveTypeFactory]): List to store primitive type factories
                related to the instance.
            enumerations (List[EnumerationTypeFactory]): List to store enumeration type factories
                related to the instance.
        """
        self.lw_version = lw_version or LionWebVersion.current_version()
        self.version = version
        self.name = name
        self.id_calculator = id_calculator or (
            lambda parent_id, name: name if parent_id is None else f"{parent_id}_{name}"
        )
        self.key_calculator = key_calculator or (
            lambda parent_key, name: name if parent_key is None else f"{parent_key}_{name}"
        )
        self.id = id or self.id_calculator(None, name)
        self.key = key or self.key_calculator(None, name)
        self.dependencies: list[Language] = list(dependencies or [])
        self.entities: list[EntityFactory] = []
        self.classifiers: list[ClassifierFactory] = []
        self.primitive_types: list[PrimitiveTypeFactory] = []
        self.enumerations: list[EnumerationTypeFactory] = []

    def build(self) -> Language:
        """
        Builds a Language object and populates its components.

        This function is responsible for creating a `Language` instance based on the
        attributes of the current object. It initializes the language with relevant
        details such as its name, id, key, version, and lion web version. Additionally,
        it builds the elements in the order in which they were declared, then populates
        the classifiers.

        Returns:
            Language: The constructed `Language` object.
        """
        language = Language(
            name=self.name,
            id=self.id,
            key=self.key,
            version=self.version,
            lion_web_version=self.lw_version,
        )

        for dependency in self.dependencies:
            language.add_dependency(dependency)

        built: dict[EntityFactory, LanguageEntity] = {}
        for entity in self.entities:
            if isinstance(entity, EnumerationTypeFactory):
                built[entity] = entity.build(language, self.id_calculator, self.key_calculator)
            else:
                built[entity] = entity.build(language)
        for classifier in self.classifiers:
            classifier.populate(
                cast(Classifier, built[classifier]), self.id_calculator, self.key_calculator, built
            )

        return language

    def concept(
        self,
        name: str,
        id: str | None = None,
        key: str | None = None,
        extends: ClassifierFactory | Concept | None = None,
        implements: list[ClassifierFactory | Interface] | None = None,
        abstract: bool = False,
        partition: bool = False,
    ) -> ClassifierFactory:
        sub = ClassifierFactory(
            "Concept",
            name,
            id=id or self.id_calculator(self.id, name),
            key=key or self.key_calculator(self.key, name),
            extends=[extends] if extends is not None else None,
            implements=implements,
            abstract=abstract,
            partition=partition,
        )
        self._add_classifier(sub)
        return sub

    def interface(
        self,
        name: str,
        id: str | None = None,
        key: str | None = None,
        extends: list[ClassifierFactory | Classifier] | None = None,
    ) -> ClassifierFactory:
        sub = ClassifierFactory(
            "Interface",
            name,
            id=id or self.id_calculator(self.id, name),
            key=key or self.key_calculator(self.key, name),
            extends=extends,
        )
        self._add_classifier(sub)
        return sub

    def annotation(
        self,
        name: str,
        annotates: ClassifierFactory | Classifier,
        id: str | None = None,
        key: str | None = None,
        extends: ClassifierFactory | Annotation | None = None,
        implements: list[ClassifierFactory | Interface] | None = None,
    ) -> ClassifierFactory:
        sub = ClassifierFactory(
            "Annotation",
            name,
            id=id or self.id_calculator(self.id, name),
            key=key or self.key_calculator(self.key, name),
            extends=[extends] if extends is not None else None,
            implements=implements,
        )
        sub.set_annotates(annotates)
        self._add_classifier(sub)
        return sub

    def primitive_type(
        self, name: str, id: str | None = None, key: str | None = None
    ) -> PrimitiveTypeFactory:
        sub = PrimitiveTypeFactory(
            name,
            id=id or self.id_calculator(self.id, name),
            key=key or self.key_calculator(self.key, name),
        )
        self.primitive_types.append(sub)
        self.entities.append(sub)
        return sub

    def enumeration(
        self,
        name: str,
        literals: list[str | LiteralData],
        id: str | None = None,
        key: str | None = None,
    ) -> EnumerationTypeFactory:
        sub = EnumerationTypeFactory(
            name,
            id=id or self.id_calculator(self.id, name),
            key=key or self.key_calculator(self.key, name),
            literals=literals,
        )
        self.enumerations.append(sub)
        self.entities.append(sub)
        return sub

    def _add_classifier(self, classifier: ClassifierFactory) -> None:
        self.classifiers.append(classifier)
        self.entities.append(classifier)
