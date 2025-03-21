from typing import Optional

from lionwebpython.language import Annotation
from lionwebpython.model.annotation_instance import AnnotationInstance
from lionwebpython.model.node import Node


class ProxyNode(Node):
    """
    This is a basic ID holder adapted as a Node. It is used as a placeholder to indicate that we
    know which Node should be used in a particular point, but at this time we cannot/do not want to
    retrieve the data necessary to properly instantiate it.
    """

    def add_annotation(self, instance: "AnnotationInstance") -> None:
        raise self.CannotDoBecauseProxyException(self.id)

    def remove_annotation(self, instance: "AnnotationInstance") -> None:
        raise self.CannotDoBecauseProxyException(self.id)

    class CannotDoBecauseProxyException(Exception):
        def __init__(self, node_id: Optional[str]):
            super().__init__(
                f"Replace the proxy node with a real node to perform this operation (nodeID: {node_id})"
            )
            self.node_id = node_id

    def __init__(self, node_id: str):
        if node_id is None:
            raise ValueError("The node ID of a ProxyNode should not be null")
        self._id = node_id

    def get_parent(self):
        raise self.CannotDoBecauseProxyException(self.id)

    def get_property_value(self, property):
        raise self.CannotDoBecauseProxyException(self.id)

    def set_property_value(self, property, value):
        raise self.CannotDoBecauseProxyException(self.id)

    def get_children(self, containment):
        raise self.CannotDoBecauseProxyException(self.id)

    def add_child(self, containment, child):
        raise self.CannotDoBecauseProxyException(self.id)

    def remove_child(self, node):
        raise self.CannotDoBecauseProxyException(self.id)

    def get_reference_values(self, reference):
        raise self.CannotDoBecauseProxyException(self.id)

    def add_reference_value(self, reference, referred_node):
        raise self.CannotDoBecauseProxyException(self.id)

    def get_id(self) -> str:
        return self._id

    def get_classifier(self):
        raise self.CannotDoBecauseProxyException(self.id)

    def get_annotations(self, annotation: Optional["Annotation"] = None):
        raise self.CannotDoBecauseProxyException(self.id)

    def get_containment_feature(self):
        raise self.CannotDoBecauseProxyException(self.id)

    def remove_child_by_index(self, containment, index: int):
        raise self.CannotDoBecauseProxyException(self.id)

    def remove_reference_value(self, reference, reference_value):
        raise self.CannotDoBecauseProxyException(self.id)

    def remove_reference_value_by_index(self, reference, index: int):
        raise self.CannotDoBecauseProxyException(self.id)

    def set_reference_values(self, reference, values):
        raise self.CannotDoBecauseProxyException(self.id)

    def __eq__(self, other):
        if not isinstance(other, ProxyNode):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"ProxyNode({self.id})"
