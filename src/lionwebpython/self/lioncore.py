from typing import TYPE_CHECKING, Dict, List, cast

if TYPE_CHECKING:
    from lionwebpython.language.concept import Concept

from lionwebpython.language.containment import Containment
from lionwebpython.language.language import Language
from lionwebpython.language.lioncore_builtins import LionCoreBuiltins
from lionwebpython.language.property import Property
from lionwebpython.language.reference import Reference
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.model.impl.m3node import M3Node
from lionwebpython.utils.id_utils import IdUtils


class LionCore:
    _instances: Dict[LionWebVersion, Language] = {}
    if TYPE_CHECKING:
        from lionwebpython.model.impl.m3node import M3Node

    @classmethod
    def get_language_entity(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ) -> "Concept":
        return cls.get_instance(lion_web_version).require_concept_by_name(
            "LanguageEntity"
        )

    @classmethod
    def get_link(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ) -> "Concept":
        return cls.get_instance(lion_web_version).require_concept_by_name("Link")

    @classmethod
    def get_classifier(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ) -> "Concept":
        return cls.get_instance(lion_web_version).require_concept_by_name("Classifier")

    @classmethod
    def get_feature(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ) -> "Concept":
        return cls.get_instance(lion_web_version).require_concept_by_name("Feature")

    @classmethod
    def get_structured_data_type(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ) -> "Concept":
        return cls.get_instance(lion_web_version).require_concept_by_name(
            "StructuredDataType"
        )

    @classmethod
    def get_field(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ) -> "Concept":
        return cls.get_instance(lion_web_version).require_concept_by_name("Field")

    @classmethod
    def get_annotation(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ) -> "Concept":
        return cls.get_instance(lion_web_version).require_concept_by_name("Annotation")

    @classmethod
    def get_concept(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ) -> "Concept":
        if not isinstance(lion_web_version, LionWebVersion):
            raise ValueError(
                f"Expected lion_web_version to be an instance of LionWebVersion but got {lion_web_version}"
            )
        return cls.get_instance(lion_web_version).require_concept_by_name("Concept")

    @classmethod
    def get_interface(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ) -> "Concept":
        return cls.get_instance(lion_web_version).require_concept_by_name("Interface")

    @classmethod
    def get_containment(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ) -> "Concept":
        return cls.get_instance(lion_web_version).require_concept_by_name("Containment")

    @classmethod
    def get_data_type(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ) -> "Concept":
        return cls.get_instance(lion_web_version).require_concept_by_name("DataType")

    @classmethod
    def get_enumeration(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ) -> "Concept":
        return cls.get_instance(lion_web_version).require_concept_by_name("Enumeration")

    @classmethod
    def get_language(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ) -> "Concept":
        return cls.get_instance(lion_web_version).require_concept_by_name("Language")

    @classmethod
    def get_reference(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ) -> "Concept":
        return cls.get_instance(lion_web_version).require_concept_by_name("Reference")

    @classmethod
    def get_property(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ) -> "Concept":
        return cls.get_instance(lion_web_version).require_concept_by_name("Property")

    @classmethod
    def get_primitive_type(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ):
        return cls.get_instance(lion_web_version).require_concept_by_name(
            "PrimitiveType"
        )

    @classmethod
    def get_enumeration_literal(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ):
        return cls.get_instance(lion_web_version).require_concept_by_name(
            "EnumerationLiteral"
        )

    @classmethod
    def get_instance(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ) -> Language:
        from lionwebpython.language.concept import Concept

        if not isinstance(lion_web_version, LionWebVersion):
            raise ValueError(
                f"Expected lion_web_version to be an instance of LionWebVersion but got {lion_web_version}"
            )
        if lion_web_version not in cls._instances:
            version_id_suffix = (
                f"-{IdUtils.clean_string(lion_web_version.value)}"
                if lion_web_version != LionWebVersion.V2023_1
                else ""
            )
            instance = Language(lion_web_version=lion_web_version, name="LionCore_M3")
            instance.set_id(f"-id-LionCore-M3{version_id_suffix}")
            instance.set_key("LionCore-M3")
            instance.set_version(lion_web_version.value)

            # Initialize concepts
            concepts = {
                name: instance.add_element(
                    Concept(lion_web_version=lion_web_version, name=name)
                )
                for name in [
                    "Annotation",
                    "Concept",
                    "Interface",
                    "Containment",
                    "DataType",
                    "Feature",
                    "Link",
                    "Property",
                    "Enumeration",
                    "EnumerationLiteral",
                    "LanguageEntity",
                    "Classifier",
                    "Language",
                    "PrimitiveType",
                    "Reference",
                ]
            }
            from lionwebpython.language.interface import Interface

            interfaces = {
                name: instance.add_element(
                    Interface(lion_web_version=lion_web_version, name=name)
                )
                for name in [
                    "IKeyed",
                ]
            }

            concepts["Concept"].set_extended_concept(concepts["Classifier"])
            concepts["Concept"].add_feature(
                Property.create_required(
                    lion_web_version=lion_web_version,
                    name="abstract",
                    type=LionCoreBuiltins.get_boolean(lion_web_version),
                    id=f"-id-Concept-abstract{version_id_suffix}",
                )
            )
            concepts["Concept"].add_feature(
                Property.create_required(
                    lion_web_version=lion_web_version,
                    name="partition",
                    type=LionCoreBuiltins.get_boolean(lion_web_version),
                    id=f"-id-Concept-partition{version_id_suffix}",
                )
            )
            concepts["Concept"].add_feature(
                Reference.create_optional(
                    lion_web_version=lion_web_version,
                    name="extends",
                    type=concepts["Concept"],
                    id=f"-id-Concept-extends{version_id_suffix}",
                )
            )
            concepts["Concept"].add_feature(
                Reference.create_multiple(
                    lion_web_version=lion_web_version,
                    name="implements",
                    type=concepts["Interface"],
                    id=f"-id-Concept-implements{version_id_suffix}",
                )
            )

            concepts["Interface"].set_extended_concept(concepts["Classifier"])
            concepts["Interface"].add_feature(
                Reference.create_multiple(
                    lion_web_version=lion_web_version,
                    name="extends",
                    type=concepts["Interface"],
                    id=f"-id-Interface-extends{version_id_suffix}",
                )
            )

            concepts["Containment"].set_extended_concept(concepts["Link"])

            concepts["DataType"].set_extended_concept(concepts["LanguageEntity"])
            concepts["DataType"].set_abstract(True)

            concepts["Enumeration"].set_extended_concept(concepts["DataType"])
            concepts["Enumeration"].add_feature(
                Containment.create_multiple(
                    lion_web_version=lion_web_version,
                    name="literals",
                    type=concepts["EnumerationLiteral"],
                ).set_id("-id-Enumeration-literals" + version_id_suffix)
            )

            concepts["EnumerationLiteral"].add_implemented_interface(
                interfaces["IKeyed"]
            )

            concepts["Feature"].set_abstract(True)
            concepts["Feature"].add_implemented_interface(interfaces["IKeyed"])
            concepts["Feature"].add_feature(
                Property.create_required(
                    lion_web_version=lion_web_version,
                    name="optional",
                    type=LionCoreBuiltins.get_boolean(lion_web_version),
                    id="-id-Feature-optional" + version_id_suffix,
                )
            )

            concepts["Classifier"].set_abstract(True)
            concepts["Classifier"].set_extended_concept(concepts["LanguageEntity"])
            concepts["Classifier"].add_feature(
                Containment.create_multiple(
                    lion_web_version=lion_web_version,
                    name="features",
                    type=concepts["Feature"],
                    id="-id-Classifier-features" + version_id_suffix,
                )
            )

            concepts["Link"].set_abstract(True)
            concepts["Link"].set_extended_concept(concepts["Feature"])
            concepts["Link"].add_feature(
                Property.create_required(
                    lion_web_version,
                    "multiple",
                    LionCoreBuiltins.get_boolean(lion_web_version),
                    "-id-Link-multiple" + version_id_suffix,
                )
            )
            concepts["Link"].add_feature(
                Reference.create_required(
                    lion_web_version,
                    "type",
                    concepts["Classifier"],
                    "-id-Link-type" + version_id_suffix,
                )
            )

            concepts["Language"].set_partition(True)
            concepts["Language"].add_implemented_interface(interfaces["IKeyed"])
            concepts["Language"].add_feature(
                Property.create_required(
                    lion_web_version,
                    "version",
                    LionCoreBuiltins.get_string(lion_web_version),
                    "-id-Language-version" + version_id_suffix,
                )
            )
            concepts["Language"].add_feature(
                Reference.create_multiple(
                    lion_web_version=lion_web_version,
                    name="dependsOn",
                    type=concepts["Language"],
                ).set_id("-id-Language-dependsOn" + version_id_suffix)
            )
            concepts["Language"].add_feature(
                Containment.create_multiple(
                    lion_web_version,
                    "entities",
                    concepts["LanguageEntity"],
                    "-id-Language-entities" + version_id_suffix,
                ).set_key("Language-entities")
            )

            concepts["LanguageEntity"].set_abstract(True)
            concepts["LanguageEntity"].add_implemented_interface(interfaces["IKeyed"])

            concepts["PrimitiveType"].set_extended_concept(concepts["DataType"])

            concepts["Property"].set_extended_concept(concepts["Feature"])
            concepts["Property"].add_feature(
                Reference.create_required(
                    lion_web_version,
                    "type",
                    concepts["DataType"],
                    "-id-Property-type" + version_id_suffix,
                ).set_key("Property-type")
            )

            concepts["Reference"].set_extended_concept(concepts["Link"])

            interfaces["IKeyed"].add_extended_interface(
                LionCoreBuiltins.get_inamed(lion_web_version)
            )
            interfaces["IKeyed"].add_feature(
                Property.create_required(
                    lion_web_version,
                    "key",
                    LionCoreBuiltins.get_string(lion_web_version),
                ).set_id("-id-IKeyed-key" + version_id_suffix)
            )

            concepts["Annotation"].set_extended_concept(concepts["Classifier"])
            concepts["Annotation"].add_feature(
                Reference.create_optional(
                    lion_web_version,
                    "annotates",
                    concepts["Classifier"],
                    "-id-Annotation-annotates" + version_id_suffix,
                )
            )
            concepts["Annotation"].add_feature(
                Reference.create_optional(
                    lion_web_version,
                    "extends",
                    concepts["Annotation"],
                    "-id-Annotation-extends" + version_id_suffix,
                )
            )
            concepts["Annotation"].add_feature(
                Reference.create_multiple(
                    lion_web_version,
                    "implements",
                    concepts["Interface"],
                    "-id-Annotation-implements" + version_id_suffix,
                )
            )

            if lion_web_version != LionWebVersion.V2023_1:
                concepts["StructuredDataType"] = Concept(
                    lion_web_version=lion_web_version, name="StructuredDataType"
                )
                instance.add_element(concepts["StructuredDataType"])
                concepts["Field"] = Concept(
                    lion_web_version=lion_web_version, name="Field"
                )
                instance.add_element(concepts["Field"])

                concepts["StructuredDataType"].add_feature(
                    Containment.create_multiple(
                        lion_web_version=lion_web_version,
                        name="fields",
                        type=concepts["Field"],
                        id="-id-StructuredDataType-fields" + version_id_suffix,
                    ).set_optional(False)
                )

                concepts["Field"].add_implemented_interface(interfaces["IKeyed"])
                concepts["Field"].add_feature(
                    Reference.create_required(
                        lion_web_version=lion_web_version,
                        name="type",
                        type=concepts["DataType"],
                        id="-id-Field-type" + version_id_suffix,
                    )
                )

            cls._check_ids(instance, version_id_suffix)
            cls._instances[lion_web_version] = instance

        return cls._instances[lion_web_version]

    @classmethod
    def _check_ids(cls, node: "M3Node", version_id_suffix: str):
        if node.get_id() is None:
            from lionwebpython.language.namespaced_entity import \
                NamespacedEntity

            if isinstance(node, NamespacedEntity):
                namespaced_entity = node
                node.set_id(
                    f"-id-{cast(str, namespaced_entity.get_name()).replace('.', '_')}{version_id_suffix}"
                )
                from lionwebpython.language.ikeyed import IKeyed

                if isinstance(node, IKeyed) and node.get_key() is None:
                    node.set_key(cast(str, namespaced_entity.get_name()))
            else:
                raise ValueError(f"Invalid node state: {node}")

        from lionwebpython.language.classifier import Classifier

        if isinstance(node, Classifier):
            for feature in node.get_features():
                if feature.get_key() is None:
                    feature.set_key(f"{node.get_name()}-{feature.get_name()}")

        # TODO: Update once get_children is implemented correctly
        for child in cls._get_children_helper(node):
            cls._check_ids(child, version_id_suffix)

    @classmethod
    def _get_children_helper(cls, node: "M3Node") -> List["M3Node"]:
        from lionwebpython.language.classifier import Classifier
        from lionwebpython.language.feature import Feature

        if isinstance(node, Language):
            return cast(List[M3Node], node.get_elements())
        elif isinstance(node, Classifier):
            return cast(List[M3Node], node.get_features())
        elif isinstance(node, Feature):
            return []
        else:
            raise NotImplementedError(f"Unsupported node type: {node}")
