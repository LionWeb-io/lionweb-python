from typing import Dict, Optional

from lionwebpython.language.concept import Concept
from lionwebpython.language.interface import Interface
from lionwebpython.language.language import Language
from lionwebpython.language.primitive_type import PrimitiveType
from lionwebpython.language.property import Property
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.utils.id_utils import IdUtils


class LionCoreBuiltins(Language):
    _instances: Dict[LionWebVersion, "LionCoreBuiltins"] = {}

    def __init__(self, lion_web_version: LionWebVersion):
        super().__init__(lion_web_version=lion_web_version, name="LionCore_builtins")
        version_id_suffix = (
            f"-{IdUtils.clean_string(lion_web_version.value)}"
            if lion_web_version != LionWebVersion.V2023_1
            else ""
        )

        self.set_id(f"LionCore-builtins{version_id_suffix}")
        self.set_key("LionCore-builtins")
        self.set_version(lion_web_version.value)

        string_type = PrimitiveType(lion_web_version, self, "String")
        PrimitiveType(lion_web_version, self, "Boolean")
        PrimitiveType(lion_web_version, self, "Integer")

        if lion_web_version == LionWebVersion.V2023_1:
            PrimitiveType(lion_web_version, self, "JSON")

        node = Concept(lion_web_version, self, "Node").set_id(
            f"LionCore-builtins-Node{version_id_suffix}"
        )
        node.set_abstract(True)

        i_named = Interface(lion_web_version, self, "INamed").set_id(
            f"LionCore-builtins-INamed{version_id_suffix}"
        )
        i_named.add_feature(
            Property.create_required(lion_web_version, "name", string_type)
            .set_id(f"LionCore-builtins-INamed-name{version_id_suffix}")
            .set_key("LionCore-builtins-INamed-name")
        )

        for element in self.get_elements():
            if element.get_id() is None:
                element.set_id(
                    f"LionCore-builtins-{element.get_name()}{version_id_suffix}"
                )
            if element.get_key() is None:
                element.set_key(f"LionCore-builtins-{element.get_name()}")

    @classmethod
    def get_instance(
        cls, lion_web_version: Optional[LionWebVersion] = None
    ) -> "LionCoreBuiltins":
        if lion_web_version is None:
            lion_web_version = LionWebVersion.current_version

        if lion_web_version not in cls._instances:
            cls._instances[lion_web_version] = LionCoreBuiltins(lion_web_version)

        return cls._instances[lion_web_version]

    @classmethod
    def get_string(
        cls, lion_web_version: Optional[LionWebVersion] = None
    ) -> PrimitiveType:
        return cls.get_instance(lion_web_version).get_primitive_type_by_name("String")

    @classmethod
    def get_integer(
        cls, lion_web_version: Optional[LionWebVersion] = None
    ) -> PrimitiveType:
        return cls.get_instance(lion_web_version).get_primitive_type_by_name("Integer")

    @classmethod
    def get_boolean(
        cls, lion_web_version: Optional[LionWebVersion] = None
    ) -> PrimitiveType:
        return cls.get_instance(lion_web_version).get_primitive_type_by_name("Boolean")

    @classmethod
    def get_inamed(cls, lion_web_version: Optional[LionWebVersion] = None) -> Interface:
        return cls.get_instance(lion_web_version).get_interface_by_name("INamed")

    @classmethod
    def get_node(cls, lion_web_version: Optional[LionWebVersion] = None) -> Concept:
        return cls.get_instance(lion_web_version).get_concept_by_name("Node")

    @classmethod
    def get_json(cls, lion_web_version: LionWebVersion) -> PrimitiveType:
        if lion_web_version != LionWebVersion.V2023_1:
            raise ValueError("JSON was present only in v2023.1")
        return cls.get_instance(lion_web_version).get_primitive_type_by_name("JSON")
