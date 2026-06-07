from dataclasses import dataclass

from lionweb.model import ClassifierInstance


@dataclass(eq=False)
class ReferenceValue:
    """A value held by a Reference, pointing to a referred node and/or carrying
    a human-readable resolve info string used to help resolve the reference.

    Attributes:
        referred: The node being referred to, if resolved.
        resolve_info: A human-readable string that can help resolve the reference.
    """

    referred: ClassifierInstance | None = None
    resolve_info: str | None = None

    def get_referred(self) -> ClassifierInstance | None:
        return self.referred

    def get_referred_id(self) -> str | None:
        return self.referred.id if self.referred else None

    def set_referred(self, referred: ClassifierInstance | None) -> None:
        self.referred = referred

    def get_resolve_info(self) -> str | None:
        return self.resolve_info

    def set_resolve_info(self, resolve_info: str | None) -> None:
        self.resolve_info = resolve_info

    def __eq__(self, other):
        if not isinstance(other, ReferenceValue):
            return False
        return self.referred == other.referred and self.resolve_info == other.resolve_info

    def __hash__(self):
        return hash((self.referred, self.resolve_info))

    def __str__(self):
        return f"ReferenceValue{{referred={'null' if self.referred is None else self.referred.id}, resolveInfo='{self.resolve_info}'}}"
