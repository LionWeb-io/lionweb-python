from lionweb.api.classifier_instance_resolver import ClassifierInstanceResolver
from lionweb.model import ClassifierInstance


class MapBasedResolver(ClassifierInstanceResolver):
    """
    This is used only during deserialization. Some nodes could be an ID that depends on their
    position, so until we place them they could be a temporarily wrong ID.
    """

    def __init__(self, instances_by_id: dict[str, ClassifierInstance] | None = None) -> None:
        """Initialize the resolver with a (copied) mapping of IDs to instances.

        Args:
            instances_by_id: The initial ID-to-instance mapping. A defensive copy
                is stored, so subsequent external mutation has no effect.
        """
        self.instances_by_id = dict(instances_by_id) if instances_by_id is not None else {}

    def resolve(self, instance_id: str) -> ClassifierInstance | None:
        """Resolve the instance by its ID.

        Args:
            instance_id: The ID of the instance to resolve.

        Returns:
            The instance if found, otherwise ``None``.
        """
        return self.instances_by_id.get(instance_id)
