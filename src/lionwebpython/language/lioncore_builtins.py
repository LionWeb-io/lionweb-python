from typing import TYPE_CHECKING, Dict, Optional, cast

from lionwebpython.language.language import Language
from lionwebpython.lionweb_version import LionWebVersion


class LionCoreBuiltins(Language):
    if TYPE_CHECKING:
        from lionwebpython.language.concept import Concept
        from lionwebpython.language.interface import Interface
        from lionwebpython.language.primitive_type import PrimitiveType
        from lionwebpython.language.property import Property
        from lionwebpython.lionweb_version import LionWebVersion
        from lionwebpython.utils.id_utils import IdUtils

    _instances: Dict["LionWebVersion", "LionCoreBuiltins"] = {}

    def __init__(self, lion_web_version: "LionWebVersion"):
        super().__init__(lion_web_version=lion_web_version, name="LionCore_builtins")
        from lionwebpython.lionweb_version import LionWebVersion
        from lionwebpython.utils.id_utils import IdUtils

        version_id_suffix = (
            f"-{IdUtils.clean_string(lion_web_version.value)}"
            if lion_web_version != LionWebVersion.V2023_1
            else ""
        )

        self.set_id(f"LionCore-builtins{version_id_suffix}")
        self.set_key("LionCore-builtins")
        self.set_version(lion_web_version.value)

        from lionwebpython.language.primitive_type import PrimitiveType

        string_type = PrimitiveType(lion_web_version, language=self, name="String")
        boolean_type = PrimitiveType(lion_web_version, language=self, name="Boolean")
        integer_type = PrimitiveType(lion_web_version, language=self, name="Integer")
        self.add_element(string_type)
        self.add_element(boolean_type)
        self.add_element(integer_type)

        if lion_web_version == LionWebVersion.V2023_1:
            json_type = PrimitiveType(lion_web_version, self, "JSON")
            self.add_element(json_type)

        from lionwebpython.lionweb_version import LionWebVersion

        if lion_web_version == LionWebVersion.V2023_1:
            PrimitiveType(lion_web_version, self, "JSON")

        from lionwebpython.language.concept import Concept

        node = Concept(lion_web_version, self, "Node").set_id(
            f"LionCore-builtins-Node{version_id_suffix}"
        )
        node.set_abstract(True)

        from lionwebpython.language.interface import Interface

        i_named = Interface(lion_web_version, self, "INamed").set_id(
            f"LionCore-builtins-INamed{version_id_suffix}"
        )
        from lionwebpython.language.property import Property

        i_named.add_feature(
            Property.create_required(
                lion_web_version=lion_web_version, name="name", type=string_type
            )
            .set_id(f"LionCore-builtins-INamed-name{version_id_suffix}")
            .set_key("LionCore-builtins-INamed-name")
        )

        for element in self.get_elements():
            if element.id is None:
                element.set_id(
                    f"LionCore-builtins-{element.get_name()}{version_id_suffix}"
                )
            if element.get_key() is None:
                element.set_key(f"LionCore-builtins-{element.get_name()}")

    @classmethod
    def get_instance(
        cls, lion_web_version: Optional["LionWebVersion"] = None
    ) -> "LionCoreBuiltins":
        if lion_web_version is None:
            from lionwebpython.lionweb_version import LionWebVersion

            lion_web_version = LionWebVersion.current_version()

        if lion_web_version not in cls._instances:
            cls._instances[lion_web_version] = LionCoreBuiltins(lion_web_version)

        return cls._instances[lion_web_version]

    @classmethod
    def get_string(
        cls, lion_web_version: Optional["LionWebVersion"] = None
    ) -> "PrimitiveType":
        from lionwebpython.language.primitive_type import PrimitiveType

        return cast(
            PrimitiveType,
            cls.get_instance(lion_web_version).get_primitive_type_by_name("String"),
        )

    @classmethod
    def get_integer(
        cls, lion_web_version: Optional["LionWebVersion"] = None
    ) -> "PrimitiveType":
        from lionwebpython.language.primitive_type import PrimitiveType

        return cast(
            PrimitiveType,
            cls.get_instance(lion_web_version).get_primitive_type_by_name("Integer"),
        )

    @classmethod
    def get_boolean(
        cls, lion_web_version: Optional["LionWebVersion"] = None
    ) -> "PrimitiveType":
        if lion_web_version is None:
            lion_web_version = LionWebVersion.current_version()
        from lionwebpython.language.primitive_type import PrimitiveType

        return cast(
            PrimitiveType,
            cls.get_instance(lion_web_version).get_primitive_type_by_name("Boolean"),
        )

    @classmethod
    def get_inamed(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ) -> "Interface":
        from lionwebpython.language.interface import Interface

        return cast(
            Interface,
            cls.get_instance(lion_web_version).get_interface_by_name("INamed"),
        )

    @classmethod
    def get_node(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ) -> "Concept":
        from lionwebpython.language.concept import Concept

        return cast(
            Concept, cls.get_instance(lion_web_version).get_concept_by_name("Node")
        )

    @classmethod
    def get_json(
        cls, lion_web_version: LionWebVersion = LionWebVersion.current_version()
    ) -> "PrimitiveType":
        from lionwebpython.lionweb_version import LionWebVersion

        if lion_web_version != LionWebVersion.V2023_1:
            raise ValueError("JSON was present only in v2023.1")
        from lionwebpython.language.primitive_type import PrimitiveType

        return cast(
            PrimitiveType,
            cls.get_instance(lion_web_version).get_primitive_type_by_name("JSON"),
        )
