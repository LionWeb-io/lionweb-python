from typing import TYPE_CHECKING, Optional, cast

from lionweb.language.feature import Feature
from lionweb.lionweb_version import LionWebVersion


class Property(Feature["Property"]):
    if TYPE_CHECKING:
        from lionweb.language.classifier import Classifier
        from lionweb.language.concept import Concept
        from lionweb.language.data_type import DataType
        from lionweb.language.debug_utils import DebugUtils
        from lionweb.lionweb_version import LionWebVersion
        from lionweb.model.classifier_instance_utils import \
            ClassifierInstanceUtils
        from lionweb.self.lioncore import LionCore

    @staticmethod
    def create_optional(**kwargs) -> "Property":
        from lionweb.lionweb_version import LionWebVersion

        lion_web_version: Optional[LionWebVersion] = LionWebVersion.current_version()
        if "lionweb_version" in kwargs:
            lion_web_version = kwargs["lionweb_version"]
        name: Optional[str] = kwargs["name"]
        from lionweb.language.data_type import DataType

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
        property_instance.optional = True
        property_instance.type = type
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
            property_instance.key = key
        property_instance.optional = False
        property_instance.type = type
        return property_instance

    def __init__(
        self,
        lion_web_version: Optional["LionWebVersion"] = None,
        name: Optional[str] = None,
        container: Optional["Classifier"] = None,
        id: Optional[str] = None,
        key: Optional[str] = None,
        type: Optional["DataType"] = None,
    ):
        super().__init__(
            lion_web_version=lion_web_version, name=name, container=container, id=id
        )
        if key:
            self.key = key
        if type:
            self.type = type

    @property
    def type(self) -> Optional["DataType"]:
        from lionweb.language.data_type import DataType

        return cast(Optional[DataType], self.get_reference_single_value("type"))

    @type.setter
    def type(self, type: Optional["DataType"]) -> None:
        if type is None:
            self.set_reference_single_value(link_name="type", value=None)
        else:
            from lionweb.model.classifier_instance_utils import \
                ClassifierInstanceUtils

            self.set_reference_single_value(
                "type", ClassifierInstanceUtils.reference_to(type)
            )

    @property
    def optional(self) -> bool:
        return cast(bool, self.get_property_value(property_name="optional"))

    @optional.setter
    def optional(self, value: bool) -> None:
        self.set_property_value(property_name="optional", value=value)

    @property
    def key(self) -> Optional[str]:
        return cast(Optional[str], self.get_property_value(property_name="key"))

    @key.setter
    def key(self, value: Optional[str]) -> None:
        self.set_property_value(property_name="key", value=value)

    def __str__(self) -> str:
        from lionweb.language.debug_utils import DebugUtils

        return f"{super().__str__()}{{qualifiedName={DebugUtils.qualified_name(self)}, type={self.type}}}"

    def __repr__(self):
        from lionweb.language.debug_utils import DebugUtils

        return f"{super().__str__()}{{qualifiedName={DebugUtils.qualified_name(self)}, type={self.type}}}"

    def get_classifier(self) -> "Concept":
        from lionweb.self.lioncore import LionCore

        return LionCore.get_property(self.get_lionweb_version())
