from typing import TYPE_CHECKING, Optional

from lionwebpython.language.link import Link


class Containment(Link["Containment"]):
    if TYPE_CHECKING:
        from lionwebpython.language.classifier import Classifier
        from lionwebpython.language.concept import Concept
        from lionwebpython.lionweb_version import LionWebVersion

    @staticmethod
    def create_optional(
        name: Optional[str] = None,
        type: Optional["Classifier"] = None,
        id: Optional[str] = None,
        key: Optional[str] = None,
    ) -> "Containment":
        containment = Containment(name=name)
        containment.set_optional(True)
        containment.set_multiple(False)
        containment.set_type(type)
        if id:
            containment.set_id(id)
        if key:
            containment.set_key(key)
        return containment

    @staticmethod
    def create_required(
        name: Optional[str] = None, type: Optional["Classifier"] = None
    ) -> "Containment":
        containment = Containment(name=name)
        containment.set_optional(False)
        containment.set_multiple(False)
        containment.set_type(type)
        return containment

    @staticmethod
    def create_multiple(
        lion_web_version: Optional["LionWebVersion"] = None,
        name: Optional[str] = None,
        type: Optional["Classifier"] = None,
        id: Optional[str] = None,
    ) -> "Containment":
        if lion_web_version is None:
            containment = Containment(name=name)
        else:
            containment = Containment(lion_web_version=lion_web_version, name=name)
        containment.set_optional(True)
        containment.set_multiple(True)
        containment.set_type(type)
        if id:
            containment.set_id(id)
        return containment

    @staticmethod
    def create_multiple_and_required(
        name: Optional[str] = None, type: Optional["Classifier"] = None
    ) -> "Containment":
        containment = Containment(name=name)
        containment.set_optional(False)
        containment.set_multiple(True)
        containment.set_type(type)
        return containment

    def __init__(
        self,
        lion_web_version: Optional["LionWebVersion"] = None,
        name: Optional[str] = None,
        id: Optional[str] = None,
        container: Optional["Classifier"] = None,
    ):
        super().__init__(
            lion_web_version=lion_web_version, name=name, id=id, container=container
        )

    def get_classifier(self) -> "Concept":
        from lionwebpython.self.lioncore import LionCore

        return LionCore.get_containment(self.get_lionweb_version())

    def __str__(self):
        return f"Containment[{self.id}]"
