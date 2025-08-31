from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from lionweb.language.concept import Concept

from lionweb.language.data_type import DataType
from lionweb.language.language import Language
from lionweb.lionweb_version import LionWebVersion


class PrimitiveType(DataType):
    def __init__(
        self,
        lion_web_version: LionWebVersion = LionWebVersion.current_version(),
        language: Optional[Language] = None,
        name: Optional[str] = None,
        id: Optional[str] = None,
        key: Optional[str] = None,
    ):
        super().__init__(lion_web_version, language, name)
        if id:
            self.set_id(id)
        if key:
            self.set_key(key)

    def get_classifier(self) -> "Concept":
        from lionweb.self.lioncore import LionCore

        return LionCore.get_primitive_type(self.get_lionweb_version())

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        name = getattr(self, "name", None)
        id_ = getattr(self, "id", None)

        key = None
        get_key = getattr(self, "get_key", None)
        if callable(get_key):
            try:
                key = get_key()
            except Exception:
                key = None
        if key is None:
            key = getattr(self, "key", None)

        lwv = None
        try:
            lwv = self.get_lionweb_version()
        except Exception:
            lwv = None

        parts = []
        if name is not None:
            parts.append(f"name={name!r}")
        if id_ is not None:
            parts.append(f"id={id_!r}")
        if key is not None:
            parts.append(f"key={key!r}")
        if lwv is not None:
            parts.append(f"lionweb_version={lwv!r}")

        return f"{cls}({', '.join(parts)})"
