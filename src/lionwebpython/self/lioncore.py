from typing import Dict, Optional

from lionwebpython.language.concept import Concept
from lionwebpython.language.containment import Containment
from lionwebpython.language.language import Language
from lionwebpython.language.lioncore_builtins import LionCoreBuiltins
from lionwebpython.language.property import Property
from lionwebpython.language.reference import Reference
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.utils.id_utils import IdUtils


class LionCore:
    _instances: Dict[LionWebVersion, Language] = {}

    @classmethod
    def get_annotation(
        cls, lion_web_version: Optional[LionWebVersion] = None
    ) -> Concept:
        return cls._get_instance(lion_web_version).require_concept_by_name("Annotation")

    @classmethod
    def get_concept(cls, lion_web_version: Optional[LionWebVersion] = None) -> Concept:
        return cls._get_instance(lion_web_version).require_concept_by_name("Concept")

    @classmethod
    def get_interface(
        cls, lion_web_version: Optional[LionWebVersion] = None
    ) -> Concept:
        return cls._get_instance(lion_web_version).require_concept_by_name("Interface")

    @classmethod
    def get_containment(
        cls, lion_web_version: Optional[LionWebVersion] = None
    ) -> Concept:
        return cls._get_instance(lion_web_version).require_concept_by_name(
            "Containment"
        )

    @classmethod
    def get_data_type(
        cls, lion_web_version: Optional[LionWebVersion] = None
    ) -> Concept:
        return cls._get_instance(lion_web_version).require_concept_by_name("DataType")

    @classmethod
    def get_enumeration(
        cls, lion_web_version: Optional[LionWebVersion] = None
    ) -> Concept:
        return cls._get_instance(lion_web_version).require_concept_by_name(
            "Enumeration"
        )

    @classmethod
    def get_language(cls, lion_web_version: Optional[LionWebVersion] = None) -> Concept:
        return cls._get_instance(lion_web_version).require_concept_by_name("Language")

    @classmethod
    def get_reference(
        cls, lion_web_version: Optional[LionWebVersion] = None
    ) -> Concept:
        return cls._get_instance(lion_web_version).require_concept_by_name("Reference")

    @classmethod
    def get_property(cls, lion_web_version: Optional[LionWebVersion] = None) -> Concept:
        return cls._get_instance(lion_web_version).require_concept_by_name("Property")

    @classmethod
    def _get_instance(
        cls, lion_web_version: Optional[LionWebVersion] = None
    ) -> Language:
        if lion_web_version is None:
            lion_web_version = LionWebVersion.current_version

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
                    "Enumeration",
                    "LanguageEntity",
                ]
            }

            concepts["Concept"].set_extended_concept(concepts["LanguageEntity"])
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

            concepts["Interface"].set_extended_concept(concepts["LanguageEntity"])
            concepts["Interface"].add_feature(
                Reference.create_multiple(
                    lion_web_version=lion_web_version,
                    name="extends",
                    type=concepts["Interface"],
                    id=f"-id-Interface-extends{version_id_suffix}",
                )
            )

            concepts["Containment"].set_extended_concept(concepts["LanguageEntity"])

            concepts["DataType"].set_extended_concept(concepts["LanguageEntity"])
            concepts["DataType"].set_abstract(True)

            concepts["Enumeration"].set_extended_concept(concepts["DataType"])
            concepts["Enumeration"].add_feature(
                Containment.create_multiple(
                    lion_web_version=lion_web_version,
                    name="literals",
                    type=concepts["LanguageEntity"],
                )
            )

            cls._instances[lion_web_version] = instance

        return cls._instances[lion_web_version]
