from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from lionwebpython.api.classifier_instance_resolver import (
        ClassifierInstanceResolver,
    )
    from lionwebpython.api.local_classifier_instance_resolver import (
        LocalClassifierInstanceResolver,
    )
    from lionwebpython.model.impl.proxy_node import ProxyNode

from lionwebpython.model.node import Node
from lionwebpython.serialization.data.serialized_classifier_instance import \
    SerializedClassifierInstance


class DeserializationStatus:
    def __init__(
        self,
        original_list: List[SerializedClassifierInstance],
        outside_instances_resolver: "ClassifierInstanceResolver",
    ):
        from lionwebpython.api.composite_classifier_instance_resolver import \
            CompositeClassifierInstanceResolver
        from lionwebpython.api.local_classifier_instance_resolver import \
            LocalClassifierInstanceResolver
        from lionwebpython.model.impl.proxy_node import ProxyNode

        self.sorted_list: List[SerializedClassifierInstance] = []
        self.nodes_to_sort = list(original_list)
        self.proxies: List[ProxyNode] = []
        self.proxies_instance_resolver = LocalClassifierInstanceResolver()
        self.global_instance_resolver = CompositeClassifierInstanceResolver(
            outside_instances_resolver, self.proxies_instance_resolver
        )

    def put_nodes_with_null_ids_in_front(self) -> None:
        null_id_nodes = [n for n in self.nodes_to_sort if n.get_id() is None]
        self.sorted_list.extend(null_id_nodes)
        self.nodes_to_sort = [n for n in self.nodes_to_sort if n.get_id() is not None]

    def place(self, node: SerializedClassifierInstance) -> None:
        self.sorted_list.append(node)
        self.nodes_to_sort.remove(node)

    def reverse(self):
        self.sorted_list.reverse()

    def how_many_sorted(self) -> int:
        return len(self.sorted_list)

    def how_many_to_sort(self) -> int:
        return len(self.nodes_to_sort)

    def get_node_to_sort(self, index: int):
        return self.nodes_to_sort[index]

    def stream_sorted(self):
        return iter(self.sorted_list)

    def resolve(self, node_id: Optional[str]) -> Optional[Node]:
        if node_id is None:
            return None
        resolved = self.global_instance_resolver.resolve(node_id)
        if resolved is None:
            return self.create_proxy(node_id)
        if isinstance(resolved, Node):
            return resolved
        raise ValueError(f"The given ID resolved to a non-node instance: {resolved}")

    def create_proxy(self, node_id: str) -> "ProxyNode":
        from lionwebpython.model.impl.proxy_node import ProxyNode

        if self.global_instance_resolver.resolve(node_id) is not None:
            raise ValueError(f"Cannot create proxy for ID {node_id} - already resolved")
        proxy_node = ProxyNode(node_id)
        self.proxies_instance_resolver.add(proxy_node)
        self.proxies.append(proxy_node)
        return proxy_node

    def get_proxies_instance_resolver(self) -> "LocalClassifierInstanceResolver":
        return self.proxies_instance_resolver
