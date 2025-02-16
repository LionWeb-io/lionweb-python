from typing import Dict

from lionwebpython.api.classifier_instance_resolver import \
    ClassifierInstanceResolver
from lionwebpython.model import ClassifierInstance


class MapBasedResolver(ClassifierInstanceResolver):
    """
    This is used only during deserialization. Some nodes could be an ID that depends on their
    position, so until we place them they could be a temporarily wrong ID.
    """

    def __init__(self, instances_by_id: Dict[str, ClassifierInstance] = {}):
        self.instances_by_id = dict(instances_by_id)

    def resolve(self, instance_id):
        """
        Resolve the instance by its ID.

        :param instance_id: The ID of the instance to resolve.
        :return: The instance if found, otherwise None.
        """
        return self.instances_by_id.get(instance_id)
