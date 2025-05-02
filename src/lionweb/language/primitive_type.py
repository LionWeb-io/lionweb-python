from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from lionweb.language.concept import Concept

from lionweb.language.data_type import DataType
from lionweb.language.language import Language
from lionweb.lionweb_version import LionWebVersion
from lionweb.self.lioncore import LionCore


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
