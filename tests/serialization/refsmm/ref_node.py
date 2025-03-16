from typing import List, Optional

from serialization.simple_node import SimpleNode

from lionwebpython.language.concept import Concept
from lionwebpython.language.reference import Reference
from lionwebpython.model.reference_value import ReferenceValue


class RefNode(SimpleNode):
    def __init__(self, id: Optional[str] = None):
        super().__init__()
        self.referred: Optional["RefNode"] = None
        if id is not None:
            self.id = id
        else:
            self.assign_random_id()

    def set_referred(self, referred: "RefNode"):
        self.referred = referred

    def get_classifier(self) -> Concept:
        from serialization.refsmm.refs_language import RefsLanguage

        return RefsLanguage.REF_NODE

    def __eq__(self, other):
        if not isinstance(other, RefNode):
            return False
        return self.referred.get_id() == other.referred.get_id()

    def __hash__(self):
        return hash(self.referred.get_id())

    def __str__(self):
        return f"RefNode{{referred={self.referred.get_id()}}}"

    def concrete_get_reference_values(
        self, reference: Reference
    ) -> List[ReferenceValue]:
        if reference.get_name() == "referred":
            if self.referred is None:
                return []
            return [ReferenceValue(self.referred, "")]
        return super().concrete_get_reference_values(reference)

    def concrete_add_reference_value(
        self, reference: Reference, referred_node: Optional[ReferenceValue]
    ):
        if reference.get_name() == "referred":
            self.referred = referred_node.referred if referred_node else None
        else:
            super().concrete_add_reference_value(reference, referred_node)
