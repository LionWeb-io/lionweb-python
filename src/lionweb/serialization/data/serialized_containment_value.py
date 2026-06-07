from dataclasses import dataclass, field

from lionweb.serialization.data.metapointer import MetaPointer


@dataclass
class SerializedContainmentValue:
    """A serialized containment feature value: a meta pointer plus the IDs of the children.

    Args:
        meta_pointer: The :class:`MetaPointer` identifying the containment feature.
        children_ids: The IDs of the contained children (``None`` entries indicate
            children with a null/missing ID).
    """

    meta_pointer: MetaPointer
    children_ids: list[str | None] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.children_ids is None:
            self.children_ids = []

    def get_meta_pointer(self) -> MetaPointer:
        return self.meta_pointer

    def set_meta_pointer(self, meta_pointer: MetaPointer) -> None:
        self.meta_pointer = meta_pointer

    def get_children_ids(self) -> list[str | None]:
        return self.children_ids.copy()

    def set_children_ids(self, value: list[str | None]) -> None:
        self.children_ids = value.copy()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SerializedContainmentValue):
            return False
        return self.meta_pointer == other.meta_pointer and self.children_ids == other.children_ids

    def __hash__(self) -> int:
        return hash((self.meta_pointer, tuple(self.children_ids)))

    def __str__(self) -> str:
        return f"SerializedContainmentValue{{meta_pointer={self.meta_pointer}, value={self.children_ids}}}"
