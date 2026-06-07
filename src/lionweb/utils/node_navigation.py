from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lionweb.model import Node


def root(nodes: list["Node"]) -> "Node":
    """Return the single root node among the given nodes.

    Args:
        nodes: The nodes to search.

    Returns:
        Node: The unique root node.

    Raises:
        ValueError: If there is not exactly one root node.
    """
    roots = [node for node in nodes if node.is_root()]
    if len(roots) != 1:
        raise ValueError(f"Expected one root, found {len(roots)}")
    return roots[0]
