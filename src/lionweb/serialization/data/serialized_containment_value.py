from typing import List, Optional

from lionweb.serialization.data.metapointer import MetaPointer


class SerializedContainmentValue:
    def __init__(self, meta_pointer: MetaPointer, children_ids: List[Optional[str]]):
        self.meta_pointer = meta_pointer
        self.children_ids = children_ids if children_ids is not None else []

    def get_meta_pointer(self) -> MetaPointer:
        return self.meta_pointer

    def set_meta_pointer(self, meta_pointer):
        self.meta_pointer = meta_pointer

    def get_children_ids(self) -> List[Optional[str]]:
        return self.children_ids.copy()

    def set_children_ids(self, value: List[Optional[str]]):
        self.children_ids = value.copy()

    def __eq__(self, other):
        if not isinstance(other, SerializedContainmentValue):
            return False
        return (
            self.meta_pointer == other.meta_pointer
            and self.children_ids == other.children_ids
        )

    def __hash__(self):
        return hash((self.meta_pointer, tuple(self.children_ids)))

    def __str__(self):
        return f"SerializedContainmentValue{{meta_pointer={self.meta_pointer}, value={self.children_ids}}}"
