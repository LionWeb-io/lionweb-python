from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Entry:
    resolve_info: Optional[str] = None
    reference: Optional[str] = None

    def __str__(self):
        return (
            f"Entry{{resolve_info='{self.resolve_info}', reference='{self.reference}'}}"
        )

    def __eq__(self, other):
        if not isinstance(other, Entry):
            return False
        return (
            self.resolve_info == other.resolve_info
            and self.reference == other.reference
        )

    def __hash__(self):
        return hash((self.resolve_info, self.reference))


class SerializedReferenceValue:
    def __init__(self, meta_pointer=None, value: Optional[List[Entry]] = None):
        self.meta_pointer = meta_pointer
        self.value = value[:] if value else []

    def get_meta_pointer(self):
        return self.meta_pointer

    def set_meta_pointer(self, meta_pointer):
        self.meta_pointer = meta_pointer

    def get_value(self) -> List[Entry]:
        return list(self.value)

    def set_value(self, value: List[Entry]):
        self.value.clear()
        self.value.extend(value)

    def add_value(self, value: Entry):
        self.value.append(value)

    def __eq__(self, other):
        if not isinstance(other, SerializedReferenceValue):
            return False
        return self.meta_pointer == other.meta_pointer and self.value == other.value

    def __hash__(self):
        return hash((self.meta_pointer, tuple(self.value)))

    def __str__(self):
        return f"SerializedReferenceValue{{meta_pointer={self.meta_pointer}, value={self.value}}}"
