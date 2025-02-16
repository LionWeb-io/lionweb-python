from typing import List, Optional

from serialization.simple_node import SimpleNode

from lionwebpython.language.concept import Concept
from lionwebpython.language.containment import Containment
from lionwebpython.model.node import Node


class ContainerNode(SimpleNode):
    def __init__(
        self, contained: Optional["ContainerNode"] = None, id: Optional[str] = None
    ):
        super().__init__()
        self.contained = contained
        if id:
            self.id = id
        else:
            self.assign_random_id()

    def get_classifier(self) -> Concept:
        from serialization.refsmm.refs_language import RefsLanguage

        return RefsLanguage.CONTAINER_NODE

    def concrete_get_children(self, containment: Containment) -> List[Node]:
        if containment.get_name() == "contained":
            return [self.contained] if self.contained else []
        return super().concrete_get_children(containment)

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, ContainerNode):
            return False
        return self.contained == other.contained

    def __hash__(self):
        return hash(self.contained)

    def __str__(self):
        contained_id = self.contained.get_id() if self.contained else "None"
        return f"ContainerNode{{contained={contained_id}}}"

    def get_contained(self) -> Optional["ContainerNode"]:
        return self.contained

    def set_contained(self, contained: "ContainerNode"):
        self.contained = contained
