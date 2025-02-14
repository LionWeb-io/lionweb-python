from typing import Optional

from lionwebpython.language.classifier import Classifier
from lionwebpython.language.concept import Concept
from lionwebpython.language.link import Link
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.self.lioncore import LionCore


class Reference(Link["Reference"]):
    @staticmethod
    def create_optional(
        name: Optional[str] = None, type: Optional[Classifier] = None
    ) -> "Reference":
        reference = Reference(name=name)
        reference.set_optional(True)
        reference.set_multiple(False)
        reference.set_type(type)
        return reference

    @staticmethod
    def create_optional_with_id(
        lion_web_version: LionWebVersion,
        name: Optional[str],
        type: Optional[Classifier],
        id: str,
    ) -> "Reference":
        if not lion_web_version:
            raise ValueError("lionWebVersion should not be null")
        if not id:
            raise ValueError("id should not be null")
        reference = Reference(lion_web_version=lion_web_version, name=name, id=id)
        reference.set_optional(True)
        reference.set_multiple(False)
        reference.set_type(type)
        return reference

    @staticmethod
    def create_required(
        name: Optional[str] = None, type: Optional[Classifier] = None
    ) -> "Reference":
        reference = Reference(name=name)
        reference.set_optional(False)
        reference.set_multiple(False)
        reference.set_type(type)
        return reference

    @staticmethod
    def create_required_with_id(
        lion_web_version: LionWebVersion,
        name: Optional[str],
        type: Optional[Classifier],
        id: str,
    ) -> "Reference":
        if not lion_web_version:
            raise ValueError("lionWebVersion should not be null")
        if not id:
            raise ValueError("id should not be null")
        reference = Reference(lion_web_version=lion_web_version, name=name, id=id)
        reference.set_optional(False)
        reference.set_multiple(False)
        reference.set_type(type)
        return reference

    @staticmethod
    def create_multiple(
        name: Optional[str] = None, type: Optional[Classifier] = None
    ) -> "Reference":
        reference = Reference(name=name)
        reference.set_optional(True)
        reference.set_multiple(True)
        reference.set_type(type)
        return reference

    @staticmethod
    def create_multiple_with_id(
        lion_web_version: LionWebVersion,
        name: Optional[str],
        type: Optional[Classifier],
        id: str,
    ) -> "Reference":
        if not lion_web_version:
            raise ValueError("lionWebVersion should not be null")
        if not id:
            raise ValueError("id should not be null")
        reference = Reference(lion_web_version=lion_web_version, name=name, id=id)
        reference.set_optional(True)
        reference.set_multiple(True)
        reference.set_type(type)
        return reference

    @staticmethod
    def create_multiple_and_required(
        name: Optional[str] = None, type: Optional[Classifier] = None
    ) -> "Reference":
        reference = Reference(name=name)
        reference.set_optional(False)
        reference.set_multiple(True)
        reference.set_type(type)
        return reference

    def __init__(
        self,
        lion_web_version: Optional[LionWebVersion] = None,
        name: Optional[str] = None,
        container: Optional[Classifier] = None,
        id: Optional[str] = None,
    ):
        if lion_web_version is not None and id is not None:
            super().__init__(lion_web_version=lion_web_version, name=name, id=id)
        elif lion_web_version is not None:
            super().__init__(
                lion_web_version=lion_web_version, name=name, container=container
            )
        elif id is not None:
            super().__init__(name=name, id=id)
        else:
            super().__init__(name=name, container=container)

    def get_classifier(self) -> Concept:
        return LionCore.get_reference(self.get_lion_web_version())
