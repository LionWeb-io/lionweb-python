from abc import ABC
from typing import TYPE_CHECKING, Generic, List, Optional, TypeVar, cast

from lionwebpython.language.ikeyed import IKeyed
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.model.classifier_instance_utils import \
    ClassifierInstanceUtils
from lionwebpython.model.impl.abstract_classifier_instance import \
    AbstractClassifierInstance
from lionwebpython.model.node import Node, is_node

T = TypeVar("T", bound="M3Node")


class M3Node(Generic[T], Node, IKeyed[T], AbstractClassifierInstance, ABC):
    if TYPE_CHECKING:
        from lionwebpython.language.containment import Containment
        from lionwebpython.language.property import Property
        from lionwebpython.language.reference import Reference
        from lionwebpython.model.classifier_instance import ClassifierInstance
        from lionwebpython.model.reference_value import ReferenceValue

    def __init__(self, lion_web_version: Optional[LionWebVersion] = None):
        AbstractClassifierInstance.__init__(self)
        if lion_web_version is not None and not isinstance(
            lion_web_version, LionWebVersion
        ):
            raise ValueError(
                f"Expected lion_web_version to be an instance of LionWebVersion or None but got {lion_web_version}"
            )
        self.lion_web_version = lion_web_version or LionWebVersion.current_version()
        self._id: Optional[str] = None
        self.parent: Optional[Node] = None
        self.property_values: dict[str, Optional[object]] = {}
        self.containment_values: dict[str, List[Node]] = {}
        from lionwebpython.model.reference_value import ReferenceValue

        self.reference_values: dict[str, List[ReferenceValue]] = {}

    def set_id(self, id: Optional[str]) -> T:
        self._id = id
        return cast(T, self)

    @property
    def id(self) -> Optional[str]:
        return self._id

    @id.setter
    def id(self, new_value):
        self._id = new_value

    def set_name(self, name: Optional[str]) -> "M3Node":
        self.set_property_value(property_name="name", value=name)
        return self

    def set_parent(self, parent: Optional["ClassifierInstance"]) -> "M3Node":
        if parent is not None and not is_node(parent):
            raise ValueError("Not supported")
        self.parent = cast(Optional[Node], parent)
        return self

    def get_root(self) -> Node:
        p = self.get_parent()
        return self if p is None else p.get_root()

    def get_parent(self) -> Optional[Node]:
        return self.parent

    def get_containment_feature(self) -> "Containment":
        raise NotImplementedError()

    def get_property_value(self, **kwargs) -> Optional[object]:
        property = kwargs.get("property")
        property_name = kwargs.get("property_name")
        if property and property_name:
            raise ValueError()
        if not property and not property_name:
            raise ValueError()
        if property_name and isinstance(property_name, str):
            return self.property_values.get(property_name)
        from lionwebpython.language.property import Property

        if property and isinstance(property, Property):
            return self.property_values.get(property.get_name())
        else:
            raise ValueError()

    def set_property_value(self, **kwargs) -> None:
        property_name = kwargs.get("property_name")
        property = kwargs.get("property")
        value = kwargs.get("value")
        from lionwebpython.language.property import Property

        if property_name and isinstance(property_name, str):
            self.property_values[property_name] = value
        elif property and isinstance(property, Property):
            self.property_values[property.get_name()] = value
        else:
            raise ValueError()

    def get_children(self, containment: Optional["Containment"] = None) -> List[Node]:
        if containment:
            name = containment.get_name()
            if name:
                return self.containment_values.get(name, [])
            else:
                raise ValueError()
        else:
            return ClassifierInstanceUtils.get_children(self)

    def add_child(self, containment: "Containment", child: Node) -> None:
        name = containment.get_name()
        if name is None:
            raise ValueError()
        if containment.is_multiple():
            self.add_containment_multiple_value(name, child)
        else:
            self.set_containment_single_value(name, child)

    def remove_child(self, **kwargs) -> None:
        raise NotImplementedError()

    def get_reference_values(self, reference: "Reference") -> List:
        name = reference.get_name()
        if name is None:
            raise ValueError()
        return self.reference_values.get(name, [])

    def add_reference_value(
        self, reference: "Reference", reference_value: "ReferenceValue"
    ) -> None:
        name = reference.get_name()
        if reference_value is None:
            return
        if name is None:
            raise ValueError()
        self.reference_values.setdefault(name, []).append(reference_value)

    def set_reference_values(self, reference: "Reference", values: List) -> None:
        name = reference.get_name()
        if name is None:
            raise ValueError()
        self.reference_values[name] = values

    def get_id(self) -> Optional[str]:
        return self._id

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.get_id()}]"

    def get_containment_single_value(self, link_name: str) -> Optional[Node]:
        values = self.containment_values.get(link_name, [])
        if not values:
            return None
        if len(values) == 1:
            return values[0]
        raise ValueError("Multiple values found")

    def get_reference_single_value(self, link_name: str) -> Optional[object]:
        values = self.reference_values.get(link_name, [])
        if not values:
            return None
        if len(values) == 1:
            return values[0].get_referred()
        raise ValueError("Multiple values found")

    def get_containment_multiple_value(self, link_name: str) -> List:
        return self.containment_values.get(link_name, [])

    def get_reference_multiple_value(self, link_name: str) -> List:
        return [rv.get_referred() for rv in self.reference_values.get(link_name, [])]

    def set_containment_single_value(self, link_name: str, value: Node) -> None:
        self.containment_values[link_name] = [value]

    def set_reference_single_value(
        self, link_name: str, value: Optional["ReferenceValue"]
    ) -> None:
        if value is None:
            self.reference_values[link_name] = []
        else:
            self.reference_values[link_name] = [value]

    def add_containment_multiple_value(self, link_name: str, value: Node) -> bool:
        """
        Adding a null value or a value already contained does not produce any change.

        Returns:
            bool: True if the addition produced a change, False otherwise.
        """
        if value is None:
            return False
        if not is_node(value):
            raise ValueError()
        if any(value is v for v in self.get_containment_multiple_value(link_name)):
            return False
        if value.id is not None and any(
            value.id == v.id for v in self.get_containment_multiple_value(link_name)
        ):
            return False
        cast(M3Node, value).set_parent(self)
        if link_name in self.containment_values:
            self.containment_values[link_name].append(value)
        else:
            self.containment_values[link_name] = [value]
        return True

    def add_reference_multiple_value(
        self, link_name: str, value: "ReferenceValue"
    ) -> None:
        self.reference_values.setdefault(link_name, []).append(value)

    def get_lionweb_version(self) -> LionWebVersion:
        return self.lion_web_version

    def __hash__(self):
        return hash(self.id)
