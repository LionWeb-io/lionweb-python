from typing import TYPE_CHECKING, Optional, TypeVar, cast

from lionwebpython.language.feature import Feature
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.model.classifier_instance_utils import \
    ClassifierInstanceUtils
from lionwebpython.model.impl.m3node import M3Node

T = TypeVar("T", bound=M3Node)


class Link(Feature[T]):
    if TYPE_CHECKING:
        from lionwebpython.language.classifier import Classifier

    def __init__(
        self,
        lion_web_version: Optional[LionWebVersion] = None,
        name: Optional[str] = None,
        id: Optional[str] = None,
        container: Optional["Classifier"] = None,
    ):
        (
            super().__init__(
                lion_web_version=lion_web_version, name=name, id=id, container=container
            )
            if lion_web_version
            else super().__init__(name=name, id=id, container=container)
        )
        self.set_multiple(False)

    def is_multiple(self) -> bool:
        return cast(
            bool, self.get_property_value(property_name="multiple", default_value=False)
        )

    def is_single(self) -> bool:
        return not self.is_multiple()

    def set_multiple(self, multiple: bool) -> T:
        self.set_property_value(property_name="multiple", value=multiple)
        return self  # type: ignore

    def get_type(self) -> Optional["Classifier"]:
        from lionwebpython.language.classifier import Classifier

        return cast(Optional[Classifier], self.get_reference_single_value("type"))

    def set_type(self, type: Optional["Classifier"]) -> T:
        if type is None:
            self.set_reference_single_value("type", None)
        else:
            self.set_reference_single_value(
                "type", ClassifierInstanceUtils.reference_to(type)
            )
        return self  # type: ignore

    @property
    def key(self):
        return cast(str, self.get_property_value(property_name="key"))

    @key.setter
    def key(self, new_value):
        self.set_property_value(property_name="key", value=new_value)

    def __str__(self) -> str:
        return f"{super().__str__()}{{qualifiedName={self.get_name()}, type={self.get_type()}}}"
