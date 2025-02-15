from typing import Optional

from lionwebpython.serialization.data.metapointer import MetaPointer


class SerializedPropertyValue:
    def __init__(self, meta_pointer: MetaPointer, value: Optional[str]):
        self.meta_pointer = meta_pointer
        self.value = value

    def get_meta_pointer(self) -> MetaPointer:
        return self.meta_pointer

    def set_meta_pointer(self, meta_pointer: MetaPointer):
        self.meta_pointer = meta_pointer

    def get_value(self) -> Optional[str]:
        return self.value

    def set_value(self, value: Optional[str]):
        self.value = value

    def __str__(self):
        return f"SerializedPropertyValue{{meta_pointer={self.meta_pointer}, value='{self.value}'}}"

    def __eq__(self, other):
        if not isinstance(other, SerializedPropertyValue):
            return False
        return self.meta_pointer == other.meta_pointer and self.value == other.value

    def __hash__(self):
        return hash((self.meta_pointer, self.value))
