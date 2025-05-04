from typing import TYPE_CHECKING, Dict, Iterable, Optional, cast

from lionweb.api.classifier_instance_resolver import ClassifierInstanceResolver

if TYPE_CHECKING:
    from lionweb.model import ClassifierInstance


class LocalClassifierInstanceResolver(ClassifierInstanceResolver):
    def __init__(self, *instances: "ClassifierInstance"):
        self.instances: Dict[str, ClassifierInstance] = {
            cast(str, instance.id): instance for instance in instances if instance.id
        }

    def add(self, instance) -> "LocalClassifierInstanceResolver":
        self.instances[instance.id] = instance
        return self

    def resolve(self, instance_id) -> Optional["ClassifierInstance"]:
        return self.instances.get(instance_id)

    def extend(self, instances: Iterable["ClassifierInstance"]) -> None:
        for instance in instances:
            self.add(instance)

    def add_tree(self, root: "ClassifierInstance"):
        self.add(root)
        for child in root.get_children():
            self.add_tree(child)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({list(self.instances.keys())})"

    __str__ = __repr__
