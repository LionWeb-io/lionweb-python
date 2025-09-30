from enum import Enum
from typing import Callable, List, Optional, TypedDict, cast

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
    id: Optional[str]
    key: Optional[str]


class LinkData(TypedDict):
    name: str
    type: "ClassifierFactory | Classifier"
    multiplicity: Multiplicity
    id: Optional[str]
    key: Optional[str]


class LiteralData(TypedDict):
    name: str
    id: Optional[str]
    key: Optional[str]


class ClassifierFactory:
    """
    A factory class for creating and managing different types of classifiers.

    This class provides mechanisms for defining classifiers, including their properties,
    references, and containments. It enables streamlined construction of models
    and metadata through a fluent interface. The supported classifier types include
    Concept, Interface, and Annotation. The factory ensures proper linking between
    classifiers and their features, leveraging optional and multiple configurations for
    flexibility.

    Attributes:
        type: The type of the classifier (one of "Concept", "Interface", "Annotation").
        name: The name of the classifier.
        id: A unique identifier for the classifier.
        key: A unique key for identifying the classifier.
        extends: A list of other ClassifierFactory or Classifier objects that this classifier extends.
    """

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
        self.references: List[LinkData] = []
        self.containments: List[LinkData] = []
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
        type: "ClassifierFactory | Classifier" = None,
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

    def containment(
        self,
        name: str,
        type: "ClassifierFactory",
        multiplicity: Multiplicity = Multiplicity.REQUIRED,
        id: Optional[str] = None,
        key: Optional[str] = None,
    ) -> "ClassifierFactory":
        self.containments.append(
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
        for data in self.references:
            reference = Reference(
                lion_web_version=classifier.lion_web_version,
                name=data["name"],
                container=classifier,
                id=data["id"] or id_calculator(classifier.id, data["name"]),
                key=data["key"] or key_calculator(classifier.key, data["name"]),
            )
            reference.set_optional(not data["multiplicity"].value["required"])
            reference.set_multiple(data["multiplicity"].value["many"])
            type_name = cast(str, data["type"].name)
            link_type = language.require_classifier_by_name(type_name)
            if link_type is None:
                raise ValueError(f"Type {type_name} not found")
            reference.set_type(link_type)
            classifier.add_feature(reference)
        for data in self.containments:
            containment = Containment(
                lion_web_version=classifier.lion_web_version,
                name=data["name"],
                container=classifier,
                id=data["id"] or id_calculator(classifier.id, data["name"]),
                key=data["key"] or key_calculator(classifier.key, data["name"]),
            )
            containment.set_optional(not data["multiplicity"].value["required"])
            containment.set_multiple(data["multiplicity"].value["many"])
            type_name = cast(str, data["type"].name)
            link_type = language.require_classifier_by_name(type_name)
            if link_type is None:
                raise ValueError(f"Type {type_name} not found")
            containment.set_type(link_type)
            classifier.add_feature(containment)
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

    def __init__(self, name: str, id: str, key: str, literals: List[str | LiteralData]):
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
                    literal_data.get("id")
                    or id_calculator(enumeration.id, literal_data["name"])
                )
                literal.set_key(
                    literal_data.get("key")
                    or key_calculator(enumeration.key, literal_data["name"])
                )
        return enumeration


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
        lw_version: Optional[LionWebVersion] = None,
        version: str = "1",
        id: Optional[str] = None,
        key: Optional[str] = None,
        id_calculator: Optional[Callable[[Optional[str], str], str]] = None,
        key_calculator: Optional[Callable[[Optional[str], str], str]] = None,
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
        """
        Builds a Language object and populates its components.

        This function is responsible for creating a `Language` instance based on the
        attributes of the current object. It initializes the language with relevant
        details such as its name, id, key, version, and lion web version. Additionally,
        it iterates over primitive types, enumerations, and classifiers to build and
        populate their corresponding components in the language.

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
        literals: List[str | LiteralData],
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
