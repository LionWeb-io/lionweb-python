from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from lionweb.model import Node


def root(nodes: List["Node"]) -> "Node":
    roots = [node for node in nodes if node.is_root()]
    if len(roots) != 1:
        raise ValueError(f"Expected one root, found {len(roots)}")
    return roots[0]
