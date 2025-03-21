from typing import Any, Dict, List, Optional, Union, cast

from lionwebpython.language.containment import Containment
from lionwebpython.language.lioncore_builtins import LionCoreBuiltins
from lionwebpython.language.reference import Reference
from lionwebpython.model.classifier_instance import ClassifierInstance
from lionwebpython.model.classifier_instance_utils import \
    ClassifierInstanceUtils
from lionwebpython.model.has_settable_parent import HasSettableParent
from lionwebpython.model.impl.abstract_classifier_instance import \
    AbstractClassifierInstance
from lionwebpython.model.node import Node
from lionwebpython.model.reference_value import ReferenceValue


class DynamicClassifierInstance(AbstractClassifierInstance, ClassifierInstance):
    """DynamicClassifierInstance can represent any instance of a Classifier.
    It allows flexible property, containment, and reference management.
    """

    def __init__(self):
        AbstractClassifierInstance.__init__(self)
        self._id: Optional[str] = None
        self.property_values: Dict[str, Any] = {}
        self.containment_values: Dict[str, List[Node]] = {}
        self.reference_values: Dict[str, List[ReferenceValue]] = {}

    def get_id(self) -> Optional[str]:
        return self._id

    def set_id(self, id: Optional[str]):
        self._id = id

    # Public methods for properties

    def get_property_value(self, **kwargs) -> Optional[object]:
        property = kwargs["property"]
        if property is None:
            raise ValueError("Property should not be null")
        if property.get_key() is None:
            raise ValueError("Property.key should not be null")
        if property not in self.get_classifier().all_properties():
            raise ValueError("Property not belonging to this classifier")

        stored_value = self.property_values.get(property.get_key())

        if (
            stored_value is None
            and property.get_type()
            == LionCoreBuiltins.get_boolean(self.get_classifier().get_lionweb_version())
            and property.is_required()
        ):
            return False

        return stored_value

    def set_property_value(self, **kwargs) -> None:
        property = kwargs["property"]
        value = kwargs["value"]
        if property is None:
            raise ValueError("Property should not be null")
        if property.get_key() is None:
            raise ValueError("Cannot assign a property with no Key specified")
        if property not in self.get_classifier().all_properties():
            raise ValueError(
                f"Property {property} does not belong to classifier {self.get_classifier()}"
            )

        if (value is None or value is False) and property.is_required():
            self.property_values.pop(property.get_key(), None)
        else:
            self.property_values[property.get_key()] = value

    # Public methods for containments

    def get_children(
        self, containment: Union[Containment, str, None] = None
    ) -> List[Node]:
        if containment is None:
            return ClassifierInstanceUtils.get_children(self)
        my_containment: Union[Containment, str]
        if isinstance(containment, str):
            tmp = self.get_classifier().get_containment_by_name(containment)
            if tmp is None:
                raise ValueError()
            my_containment = tmp
        else:
            my_containment = containment
        if my_containment.get_key() is None:
            raise ValueError("Containment.key should not be null")
        if my_containment not in self.get_classifier().all_containments():
            raise ValueError("Containment not belonging to this concept")

        return self.containment_values.get(my_containment.get_key(), [])

    def add_child(self, containment: Union[Containment, str], child: Node):
        if containment is None or child is None:
            raise ValueError("Containment and child should not be null")
        my_containment: Optional[Containment]
        if isinstance(containment, str):
            my_containment = cast(
                Containment,
                self.get_classifier().get_containment_by_name(cast(str, containment)),
            )
        else:
            my_containment = cast(Containment, containment)
        if my_containment.is_multiple():
            self._add_containment(my_containment, child)
        else:
            self._set_containment_single_value(my_containment, child)

    def remove_child(self, **kwargs) -> None:
        node = kwargs["child"]
        for key, children in self.containment_values.items():
            if node in children:
                children.remove(node)
                if isinstance(node, HasSettableParent):
                    node.set_parent(None)
                return
        raise ValueError("The given node is not a child of this node")

    def remove_child_by_index(self, containment: Containment, index: int):
        if containment is None:
            raise ValueError("Containment should not be null")
        if containment.get_key() is None:
            raise ValueError("Containment.key should not be null")
        if containment not in self.get_classifier().all_containments():
            raise ValueError("Containment not belonging to this concept")

        children = self.containment_values.get(containment.get_key(), [])
        if len(children) > index:
            del children[index]
        else:
            raise ValueError(f"Invalid index {index} when children are {len(children)}")

    # Public methods for references

    def get_reference_values(self, reference: Reference) -> List[ReferenceValue]:
        if reference is None:
            raise ValueError("Reference should not be null")
        if reference.get_key() is None:
            raise ValueError("Reference.key should not be null")
        if reference not in self.get_classifier().all_references():
            raise ValueError("Reference not belonging to this concept")

        return self.reference_values.get(reference.get_key(), [])

    def add_reference_value(
        self, reference: Reference, value: Optional[ReferenceValue]
    ):
        if reference is None:
            raise ValueError("Reference should not be null")
        if reference.is_multiple():
            if value is not None:
                self._add_reference_multiple_value(reference, value)
        else:
            self._set_reference_single_value(reference, value)

    def remove_reference_value(
        self, reference: Reference, reference_value: Optional[ReferenceValue]
    ):
        if reference is None:
            raise ValueError("Reference should not be null")
        if reference.get_key() is None:
            raise ValueError("Reference.key should not be null")
        if reference not in self.get_classifier().all_references():
            raise ValueError("Reference not belonging to this concept")

        reference_values = self.reference_values.get(reference.get_key(), [])
        for i, rv in enumerate(reference_values):
            if reference_value is None and rv is None:
                del reference_values[i]
                return
            if reference_value == rv:
                del reference_values[i]
                return
        raise ValueError(
            f"The given reference value could not be found under reference {reference.get_name()}"
        )

    def remove_reference_value_by_index(self, reference: Reference, index: int):
        if reference is None:
            raise ValueError("Reference should not be null")
        if reference.get_key() is None:
            raise ValueError("Reference.key should not be null")
        if reference not in self.get_classifier().all_references():
            raise ValueError("Reference not belonging to this classifier")

        reference_values = self.reference_values.get(reference.get_key(), [])
        if len(reference_values) > index:
            del reference_values[index]
        else:
            raise ValueError(
                f"Invalid index {index} when reference values are {len(reference_values)}"
            )

    def set_reference_values(self, reference: Reference, values: List[ReferenceValue]):
        if reference is None:
            raise ValueError("Reference should not be null")
        if reference.get_key() is None:
            raise ValueError("Reference.key should not be null")
        if reference not in self.get_classifier().all_references():
            raise ValueError("Reference not belonging to this classifier")

        self.reference_values[reference.get_key()] = values

    # Private methods for containments

    def _add_containment(self, containment: Containment, value: Node):
        assert containment.is_multiple()
        if isinstance(value, HasSettableParent):
            value.set_parent(self)
        self.containment_values.setdefault(containment.get_key(), []).append(value)

    def _set_containment_single_value(
        self, containment: Containment, value: Optional[Node]
    ):
        prev_value = self.containment_values.get(containment.get_key())
        if prev_value:
            for child in list(prev_value):
                self.remove_child(child=child)

        if value is None:
            self.containment_values.pop(containment.get_key(), None)
        else:
            if isinstance(value, HasSettableParent):
                value.set_parent(self)
            self.containment_values[containment.get_key()] = [value]

    # Private methods for references

    def _set_reference_single_value(
        self, reference: Reference, value: Optional[ReferenceValue]
    ):
        if value is None:
            self.reference_values.pop(reference.get_key(), None)
        else:
            self.reference_values[reference.get_key()] = [value]

    def _add_reference_multiple_value(
        self, reference: Reference, reference_value: ReferenceValue
    ):
        assert reference.is_multiple()
        if reference_value is not None:
            self.reference_values.setdefault(reference.get_key(), []).append(
                reference_value
            )
