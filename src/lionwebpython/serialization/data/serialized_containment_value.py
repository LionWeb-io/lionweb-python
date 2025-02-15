from typing import List

from lionwebpython.serialization.data.metapointer import MetaPointer


class SerializedContainmentValue:
    def __init__(self, meta_pointer: MetaPointer, value: List[str]):
        self.meta_pointer = meta_pointer
        self.value = value if value is not None else []

    def get_meta_pointer(self) -> MetaPointer:
        return self.meta_pointer

    def set_meta_pointer(self, meta_pointer):
        self.meta_pointer = meta_pointer

    def get_value(self) -> List[str]:
        return self.value.copy()

    def set_value(self, value: List[str]):
        self.value = value.copy()

    def __eq__(self, other):
        if not isinstance(other, SerializedContainmentValue):
            return False
        return self.meta_pointer == other.meta_pointer and self.value == other.value

    def __hash__(self):
        return hash((self.meta_pointer, tuple(self.value)))

    def __str__(self):
        return f"SerializedContainmentValue{{meta_pointer={self.meta_pointer}, value={self.value}}}"
