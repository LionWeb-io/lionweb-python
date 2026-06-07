from dataclasses import dataclass

from lionweb.serialization.data.metapointer import MetaPointer


@dataclass
class SerializedReferenceValueEntry:
    resolve_info: str | None = None
    reference: str | None = None

    def __init__(self, resolve_info: str | None, reference: str | None):
        self.resolve_info = resolve_info
        self.reference = reference

    def __str__(self):
        return f"Entry{{resolve_info='{self.resolve_info}', reference='{self.reference}'}}"

    def __eq__(self, other):
        if not isinstance(other, SerializedReferenceValueEntry):
            return False
        return self.resolve_info == other.resolve_info and self.reference == other.reference

    def __hash__(self):
        return hash((self.resolve_info, self.reference))


class SerializedReferenceValue:
    """A serialized reference feature value: a meta pointer plus the list of reference entries.

    Args:
        meta_pointer: The :class:`MetaPointer` identifying the reference feature, if known.
        value: The list of :class:`SerializedReferenceValueEntry` targets for this reference.
    """

    def __init__(
        self,
        meta_pointer: MetaPointer | None = None,
        value: list[SerializedReferenceValueEntry] | None = None,
    ):
        self.meta_pointer = meta_pointer
        self.value = value[:] if value else []

    def get_meta_pointer(self) -> MetaPointer | None:
        return self.meta_pointer

    def set_meta_pointer(self, meta_pointer: MetaPointer | None) -> None:
        self.meta_pointer = meta_pointer

    def get_value(self) -> list[SerializedReferenceValueEntry]:
        return list(self.value)

    def set_value(self, value: list[SerializedReferenceValueEntry]) -> None:
        self.value.clear()
        self.value.extend(value)

    def add_value(self, value: SerializedReferenceValueEntry) -> None:
        self.value.append(value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SerializedReferenceValue):
            return False
        return self.meta_pointer == other.meta_pointer and self.value == other.value

    def __hash__(self) -> int:
        return hash((self.meta_pointer, tuple(self.value)))

    def __str__(self) -> str:
        return f"SerializedReferenceValue{{meta_pointer={self.meta_pointer}, value={self.value}}}"
