from typing import List

from serialization.simple_node import SimpleNode
from serialization.simplemath.int_literal import IntLiteral

from lionwebpython.language.concept import Concept
from lionwebpython.language.containment import Containment
from lionwebpython.model.node import Node


class Sum(SimpleNode):
    def __init__(self, left: IntLiteral, right: IntLiteral, id: str = None):
        super().__init__()
        self.left = left
        self.right = right
        if id:
            self.id = id
        else:
            self.assign_random_id()

    def get_classifier(self) -> Concept:
        from serialization.simplemath.simple_math_language import \
            SimpleMathLanguage

        return SimpleMathLanguage.SUM

    def __eq__(self, other):
        if not isinstance(other, Sum):
            return False
        return (
            self.id == other.id
            and self.left == other.left
            and self.right == other.right
        )

    def __hash__(self):
        return hash((self.left, self.right))

    def __str__(self):
        return f"Sum{{left={self.left}, right={self.right}}}"

    def concrete_get_children(self, containment: Containment) -> List[Node]:
        if containment.get_name() == "left":
            return [self.left]
        elif containment.get_name() == "right":
            return [self.right]
        return super().concrete_get_children(containment)

    def add_child(self, containment, child):
        if containment.get_name() == "left":
            self.left = child
        elif containment.get_name() == "right":
            self.right = child
        else:
            raise ValueError()
