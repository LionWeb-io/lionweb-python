from typing import Optional, cast

from lionwebpython.language.classifier import Classifier
from lionwebpython.language.concept import Concept
from lionwebpython.language.data_type import DataType
from lionwebpython.language.debug_utils import DebugUtils
from lionwebpython.language.feature import Feature
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.model.classifier_instance_utils import \
    ClassifierInstanceUtils
from lionwebpython.self.lioncore import LionCore


class Property(Feature["Property"]):

    @staticmethod
    def create_optional(**kwargs) -> "Property":
        lion_web_version: Optional[LionWebVersion] = kwargs["lion_web_version"]
        name: Optional[str] = kwargs["name"]
        type: Optional[DataType] = kwargs["type"]
        id: Optional[str] = kwargs["id"]
        if id is not None and not isinstance(id, str):
            raise ValueError("id should not be null")
        property_instance = (
            Property(lion_web_version, name, None, id)
            if lion_web_version
            else Property(
                lion_web_version=lion_web_version, name=name, id=id, type=type
            )
        )
        property_instance.set_optional(True)
        property_instance.set_type(type)
        return property_instance

    @staticmethod
    def create_required(
        lion_web_version: Optional[LionWebVersion] = None,
        name: Optional[str] = None,
        type: Optional[DataType] = None,
        id: Optional[str] = None,
    ) -> "Property":
        if id is not None and not isinstance(id, str):
            raise ValueError("id should not be null")
        property_instance = (
            Property(lion_web_version=lion_web_version, name=name, id=id)
            if lion_web_version
            else Property(name=name, id=id)
        )
        property_instance.set_optional(False)
        property_instance.set_type(type)
        return property_instance

    def __init__(
        self,
        lion_web_version: Optional[LionWebVersion] = None,
        name: Optional[str] = None,
        container: Optional[Classifier] = None,
        id: Optional[str] = None,
        type: Optional[DataType] = None,
    ):
        (
            super().__init__(lion_web_version, name, container, id)
            if lion_web_version
            else super().__init__(name=name, container=container, id=id)
        )

    def get_type(self) -> Optional[DataType]:
        return cast(Optional[DataType], self.get_reference_single_value("type"))

    def set_type(self, type: Optional[DataType]) -> "Property":
        if type is None:
            self.set_reference_single_value(link_name="type", value=None)
        else:
            self.set_reference_single_value(
                "type", ClassifierInstanceUtils.reference_to(type)
            )
        return self

    def __str__(self) -> str:
        return f"{super().__str__()}{{qualifiedName={DebugUtils.qualified_name(self)}, type={self.get_type()}}}"

    def get_classifier(self) -> Concept:
        return LionCore.get_property(self.get_lion_web_version())
