from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lionweb.api.classifier_instance_resolver import (
        ClassifierInstanceResolver,
    )
    from lionweb.api.local_classifier_instance_resolver import (
        LocalClassifierInstanceResolver,
    )
    from lionweb.model.impl.proxy_node import ProxyNode

from lionweb.model.node import Node
from lionweb.serialization.data.serialized_classifier_instance import SerializedClassifierInstance


class DeserializationStatus:
    """Tracks the progress of sorting and resolving instances during deserialization.

    Maintains the list of serialized instances still to be sorted (leaves first),
    the resulting sorted list, and any proxy nodes created for unavailable
    referenced/parent instances.
    """

    def __init__(
        self,
        original_list: list[SerializedClassifierInstance],
        outside_instances_resolver: "ClassifierInstanceResolver",
    ) -> None:
        """Initialize the deserialization status.

        Args:
            original_list: The serialized instances to sort and deserialize.
            outside_instances_resolver: Resolver for instances outside the chunk being deserialized.
        """
        from lionweb.api.composite_classifier_instance_resolver import (
            CompositeClassifierInstanceResolver,
        )
        from lionweb.api.local_classifier_instance_resolver import LocalClassifierInstanceResolver
        from lionweb.model.impl.proxy_node import ProxyNode

        self.sorted_list: list[SerializedClassifierInstance] = []
        self.nodes_to_sort = list(original_list)
        self.proxies: list[ProxyNode] = []
        self.proxies_instance_resolver = LocalClassifierInstanceResolver()
        self.global_instance_resolver = CompositeClassifierInstanceResolver(
            outside_instances_resolver, self.proxies_instance_resolver
        )

    def put_nodes_with_null_ids_in_front(self) -> None:
        """Move all instances with a ``None`` ID to the front of the sorted list."""
        null_id_nodes = [n for n in self.nodes_to_sort if n.id is None]
        self.sorted_list.extend(null_id_nodes)
        self.nodes_to_sort = [n for n in self.nodes_to_sort if n.id is not None]

    def place(self, node: SerializedClassifierInstance) -> None:
        """Move an instance from the to-sort list to the sorted list.

        Args:
            node: The serialized instance to place.
        """
        self.sorted_list.append(node)
        self.nodes_to_sort.remove(node)

    def reverse(self) -> None:
        """Reverse the sorted list in place."""
        self.sorted_list.reverse()

    def how_many_sorted(self) -> int:
        return len(self.sorted_list)

    def how_many_to_sort(self) -> int:
        return len(self.nodes_to_sort)

    def get_node_to_sort(self, index: int) -> SerializedClassifierInstance:
        return self.nodes_to_sort[index]

    def stream_sorted(self):
        return iter(self.sorted_list)

    def resolve(self, node_id: str | None) -> Node | None:
        """Resolve a node by ID, creating a proxy if it cannot be found.

        Args:
            node_id: The ID of the node to resolve, or ``None``.

        Returns:
            The resolved node, a newly created proxy node, or ``None`` if
            ``node_id`` is ``None``.

        Raises:
            ValueError: If the given ID resolves to a non-node instance.
        """
        if node_id is None:
            return None
        resolved = self.global_instance_resolver.resolve(node_id)
        if resolved is None:
            return self.create_proxy(node_id)
        if isinstance(resolved, Node):
            return resolved
        raise ValueError(f"The given ID resolved to a non-node instance: {resolved}")

    def create_proxy(self, node_id: str) -> "ProxyNode":
        """Create and register a proxy node for an ID that cannot otherwise be resolved.

        Args:
            node_id: The ID the proxy node should represent.

        Returns:
            The newly created proxy node.

        Raises:
            ValueError: If the ID is already resolvable (a proxy would be redundant).
        """
        from lionweb.model.impl.proxy_node import ProxyNode

        if self.global_instance_resolver.resolve(node_id) is not None:
            raise ValueError(f"Cannot create proxy for ID {node_id} - already resolved")
        proxy_node = ProxyNode(node_id)
        self.proxies_instance_resolver.add(proxy_node)
        self.proxies.append(proxy_node)
        return proxy_node

    def get_proxies_instance_resolver(self) -> "LocalClassifierInstanceResolver":
        return self.proxies_instance_resolver
