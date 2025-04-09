from typing import TYPE_CHECKING, Optional, cast

from lionwebpython.language.feature import Feature
from lionwebpython.lionweb_version import LionWebVersion


class Property(Feature["Property"]):
    if TYPE_CHECKING:
        from lionwebpython.language.classifier import Classifier
        from lionwebpython.language.concept import Concept
        from lionwebpython.language.data_type import DataType
        from lionwebpython.language.debug_utils import DebugUtils
        from lionwebpython.lionweb_version import LionWebVersion
        from lionwebpython.model.classifier_instance_utils import \
            ClassifierInstanceUtils
        from lionwebpython.self.lioncore import LionCore

    @staticmethod
    def create_optional(**kwargs) -> "Property":
        from lionwebpython.lionweb_version import LionWebVersion

        lion_web_version: Optional[LionWebVersion] = LionWebVersion.current_version()
        if "lionweb_version" in kwargs:
            lion_web_version = kwargs["lionweb_version"]
        name: Optional[str] = kwargs["name"]
        from lionwebpython.language.data_type import DataType

        type: Optional[DataType] = kwargs["type"]
        id = None
        if "id" in kwargs:
            id = kwargs["id"]
        if id is not None and not isinstance(id, str):
            raise ValueError("id should not be null")
        property_instance = (
            Property(lion_web_version, name, None, id)
            if lion_web_version
            else Property(
                lion_web_version=lion_web_version,
                name=name,
                id=id,
            )
        )
        property_instance.set_optional(True)
        property_instance.set_type(type)
        return property_instance

    @staticmethod
    def create_required(
        lion_web_version: Optional["LionWebVersion"] = None,
        name: Optional[str] = None,
        type: Optional["DataType"] = None,
        id: Optional[str] = None,
        key: Optional[str] = None,
    ) -> "Property":
        if id is not None and not isinstance(id, str):
            raise ValueError("id should not be null")
        property_instance = (
            Property(lion_web_version=lion_web_version, name=name, id=id)
            if lion_web_version
            else Property(name=name, id=id)
        )
        if key is not None:
            property_instance.set_key(key)
        property_instance.set_optional(False)
        property_instance.set_type(type)
        return property_instance

    def __init__(
        self,
        lion_web_version: Optional["LionWebVersion"] = None,
        name: Optional[str] = None,
        container: Optional["Classifier"] = None,
        id: Optional[str] = None,
    ):
        super().__init__(
            lion_web_version=lion_web_version, name=name, container=container, id=id
        )

    def get_type(self) -> Optional["DataType"]:
        from lionwebpython.language.data_type import DataType

        return cast(Optional[DataType], self.get_reference_single_value("type"))

    def set_type(self, type: Optional["DataType"]) -> "Property":
        if type is None:
            self.set_reference_single_value(link_name="type", value=None)
        else:
            from lionwebpython.model.classifier_instance_utils import \
                ClassifierInstanceUtils

            self.set_reference_single_value(
                "type", ClassifierInstanceUtils.reference_to(type)
            )
        return self

    def __str__(self) -> str:
        from lionwebpython.language.debug_utils import DebugUtils

        return f"{super().__str__()}{{qualifiedName={DebugUtils.qualified_name(self)}, type={self.get_type()}}}"

    def __repr__(self):
        from lionwebpython.language.debug_utils import DebugUtils

        return f"{super().__str__()}{{qualifiedName={DebugUtils.qualified_name(self)}, type={self.get_type()}}}"

    def get_classifier(self) -> "Concept":
        from lionwebpython.self.lioncore import LionCore

        return LionCore.get_property(self.get_lionweb_version())
