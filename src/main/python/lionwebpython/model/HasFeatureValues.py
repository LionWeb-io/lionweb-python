from abc import ABC, abstractmethod
from typing import List, Optional


class HasFeatureValues(ABC):
    """
    Interface for objects that have feature values.
    """

    @abstractmethod
    def get_property_value(self, property: 'Property') -> Optional[object]:
        """
        Get the property value associated with the specified property.
        """
        pass

    @abstractmethod
    def set_property_value(self, property: 'Property', value: Optional[object]):
        """
        Set the property value for the given property.
        Raises:
            ValueError: If the value is not compatible with the property type.
        """
        pass

    @abstractmethod
    def get_children(self, containment: 'Containment') -> List['Node']:
        """
        Return all Nodes directly contained under the specified Containment relation.
        """
        pass

    @abstractmethod
    def add_child(self, containment: 'Containment', child: 'Node'):
        """
        Add a child to the specified Containment relation.
        Raises:
            ValueError: If the child's concept is not compatible.
            RuntimeError: If the Containment does not allow multiple values and already has a value.
        """
        pass

    @abstractmethod
    def remove_child(self, node: 'Node'):
        """
        Remove the given child, making it a dangling Node.
        Raises:
            ValueError: If the specified Node is not a child of this Node.
        """
        pass

    @abstractmethod
    def remove_child_at(self, containment: 'Containment', index: int):
        """
        Remove the child at the given index under the specified Containment relation.
        Raises:
            ValueError: If there is no match.
        """
        pass

    @abstractmethod
    def get_reference_values(self, reference: 'Reference') -> List['ReferenceValue']:
        """
        Return the list of reference values associated with the specified Reference.
        """
        pass

    @abstractmethod
    def add_reference_value(self, reference: 'Reference', referred_node: Optional['ReferenceValue']):
        """
        Add a Node reference under the given Reference.

        If the Reference is not multiple, any previous value will be replaced.
        Raises:
            ValueError: If the Node is not part of the Model or incompatible with the Reference target.
        """
        pass

    @abstractmethod
    def remove_reference_value(self, reference: 'Reference', reference_value: Optional['ReferenceValue']):
        """
        Remove the first matching reference value.
        Raises:
            ValueError: If there is no match.
        """
        pass

    @abstractmethod
    def remove_reference_value_at(self, reference: 'Reference', index: int):
        """
        Remove the reference value at the specified index.
        Raises:
            ValueError: If there is no match.
        """
        pass

    @abstractmethod
    def set_reference_values(self, reference: 'Reference', values: List['ReferenceValue']):
        """
        Set the reference values for a given Reference.
        """
        pass
