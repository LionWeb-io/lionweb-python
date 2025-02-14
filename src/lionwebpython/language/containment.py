from typing import Optional

from lionwebpython.language.classifier import Classifier
from lionwebpython.language.concept import Concept
from lionwebpython.language.link import Link
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.self.lioncore import LionCore


class Containment(Link["Containment"]):
    @staticmethod
    def create_optional(
        name: Optional[str] = None,
        type: Optional[Classifier] = None,
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
        name: Optional[str] = None, type: Optional[Classifier] = None
    ) -> "Containment":
        containment = Containment(name=name)
        containment.set_optional(False)
        containment.set_multiple(False)
        containment.set_type(type)
        return containment

    @staticmethod
    def create_multiple(
        lion_web_version: Optional[LionWebVersion] = None,
        name: Optional[str] = None,
        type: Optional[Classifier] = None,
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
        name: Optional[str] = None, type: Optional[Classifier] = None
    ) -> "Containment":
        containment = Containment(name=name)
        containment.set_optional(False)
        containment.set_multiple(True)
        containment.set_type(type)
        return containment

    def __init__(
        self,
        lion_web_version: Optional[LionWebVersion] = None,
        name: Optional[str] = None,
        id: Optional[str] = None,
        container: Optional[Classifier] = None,
    ):
        if lion_web_version is not None and name is not None and id is not None:
            super().__init__(lion_web_version, name, id)
        elif lion_web_version is not None and name is not None:
            super().__init__(lion_web_version, name, None)
        elif name is not None and id is not None:
            super().__init__(name=name, id=id)
        elif name is not None:
            super().__init__(name=name, container=container)
        else:
            super().__init__()

    def get_classifier(self) -> Concept:
        return LionCore.get_containment(self.get_lion_web_version())
