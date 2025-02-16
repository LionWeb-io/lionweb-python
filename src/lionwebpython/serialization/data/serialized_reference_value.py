from dataclasses import dataclass
from typing import List, Optional

from lionwebpython.serialization.data.metapointer import MetaPointer


@dataclass
class SerializedReferenceValueEntry:
    resolve_info: Optional[str] = None
    reference: Optional[str] = None

    def __init__(self, resolve_info: Optional[str], reference: Optional[str]):
        self.resolve_info = resolve_info
        self.reference = reference

    def __str__(self):
        return (
            f"Entry{{resolve_info='{self.resolve_info}', reference='{self.reference}'}}"
        )

    def __eq__(self, other):
        if not isinstance(other, SerializedReferenceValueEntry):
            return False
        return (
            self.resolve_info == other.resolve_info
            and self.reference == other.reference
        )

    def __hash__(self):
        return hash((self.resolve_info, self.reference))


class SerializedReferenceValue:
    def __init__(
        self,
        meta_pointer=None,
        value: Optional[List[SerializedReferenceValueEntry]] = None,
    ):
        self.meta_pointer = meta_pointer
        self.value = value[:] if value else []

    def get_meta_pointer(self) -> MetaPointer:
        return self.meta_pointer

    def set_meta_pointer(self, meta_pointer):
        self.meta_pointer = meta_pointer

    def get_value(self) -> List[SerializedReferenceValueEntry]:
        return list(self.value)

    def set_value(self, value: List[SerializedReferenceValueEntry]):
        self.value.clear()
        self.value.extend(value)

    def add_value(self, value: SerializedReferenceValueEntry):
        self.value.append(value)

    def __eq__(self, other):
        if not isinstance(other, SerializedReferenceValue):
            return False
        return self.meta_pointer == other.meta_pointer and self.value == other.value

    def __hash__(self):
        return hash((self.meta_pointer, tuple(self.value)))

    def __str__(self):
        return f"SerializedReferenceValue{{meta_pointer={self.meta_pointer}, value={self.value}}}"
