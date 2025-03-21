from typing import Optional

from lionwebpython.model.node import Node


class ReferenceValue:
    def __init__(
        self, referred: Optional[Node] = None, resolve_info: Optional[str] = None
    ):
        self.referred = referred
        self.resolve_info = resolve_info

    def get_referred(self) -> Optional[Node]:
        return self.referred

    def get_referred_id(self) -> Optional[str]:
        return self.referred.id if self.referred else None

    def set_referred(self, referred: Optional[Node]):
        self.referred = referred

    def get_resolve_info(self) -> Optional[str]:
        return self.resolve_info

    def set_resolve_info(self, resolve_info: Optional[str]):
        self.resolve_info = resolve_info

    def __eq__(self, other):
        if not isinstance(other, ReferenceValue):
            return False
        return (
            self.referred == other.referred and self.resolve_info == other.resolve_info
        )

    def __hash__(self):
        return hash((self.referred, self.resolve_info))

    def __str__(self):
        return f"ReferenceValue{{referred={'null' if self.referred is None else self.referred.id}, resolveInfo='{self.resolve_info}'}}"
