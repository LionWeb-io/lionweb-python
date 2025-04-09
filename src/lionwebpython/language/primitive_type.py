from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from lionwebpython.language.concept import Concept

from lionwebpython.language.data_type import DataType
from lionwebpython.language.language import Language
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.self.lioncore import LionCore


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
        return LionCore.get_primitive_type(self.get_lionweb_version())
