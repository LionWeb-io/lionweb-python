from typing import TYPE_CHECKING, Optional

from lionwebpython.language.link import Link


class Reference(Link["Reference"]):
    if TYPE_CHECKING:
        from lionwebpython.language.classifier import Classifier
        from lionwebpython.language.concept import Concept
        from lionwebpython.lionweb_version import LionWebVersion
        from lionwebpython.self.lioncore import LionCore

    @staticmethod
    def create_optional(
        lion_web_version: Optional["LionWebVersion"] = None,
        name: Optional[str] = None,
        type: Optional["Classifier"] = None,
        id: Optional[str] = None,
    ) -> "Reference":
        if lion_web_version is None:
            from lionwebpython.lionweb_version import LionWebVersion

            lion_web_version = LionWebVersion.current_version()
        reference = Reference(name=name)
        reference.set_optional(True)
        reference.set_multiple(False)
        reference.set_type(type)
        reference.set_id(id)
        return reference

    @staticmethod
    def create_required(
        lion_web_version: Optional["LionWebVersion"] = None,
        name: Optional[str] = None,
        type: Optional["Classifier"] = None,
        id: Optional[str] = None,
    ) -> "Reference":
        from lionwebpython.lionweb_version import LionWebVersion

        reference = Reference(
            lion_web_version=lion_web_version or LionWebVersion.current_version(),
            name=name,
        )
        reference.set_optional(False)
        reference.set_multiple(False)
        reference.set_type(type)
        reference.set_id(id)
        return reference

    @staticmethod
    def create_multiple(
        lion_web_version: Optional["LionWebVersion"] = None,
        name: Optional[str] = None,
        type: Optional["Classifier"] = None,
        id: Optional[str] = None,
    ) -> "Reference":
        from lionwebpython.lionweb_version import LionWebVersion

        reference = Reference(
            lion_web_version=lion_web_version or LionWebVersion.current_version(),
            name=name,
            id=id,
        )
        reference.set_optional(True)
        reference.set_multiple(True)
        reference.set_type(type)
        return reference

    @staticmethod
    def create_multiple_and_required(
        name: Optional[str] = None, type: Optional["Classifier"] = None
    ) -> "Reference":
        reference = Reference(name=name)
        reference.set_optional(False)
        reference.set_multiple(True)
        reference.set_type(type)
        return reference

    def __init__(
        self,
        lion_web_version: Optional["LionWebVersion"] = None,
        name: Optional[str] = None,
        container: Optional["Classifier"] = None,
        id: Optional[str] = None,
    ):
        from lionwebpython.language.classifier import Classifier

        if container and not isinstance(container, Classifier):
            raise ValueError(f"Invalid parameter container received: {container}")
        if lion_web_version is not None and id is not None:
            from lionwebpython.lionweb_version import LionWebVersion

            super().__init__(
                lion_web_version=lion_web_version or LionWebVersion.current_version(),
                name=name,
                id=id,
            )
        elif lion_web_version is not None:
            super().__init__(
                lion_web_version=lion_web_version, name=name, container=container
            )
        elif id is not None:
            super().__init__(name=name, id=id)
        else:
            super().__init__(name=name, container=container)

    def get_classifier(self) -> "Concept":
        from lionwebpython.self.lioncore import LionCore

        return LionCore.get_reference(self.get_lionweb_version())
