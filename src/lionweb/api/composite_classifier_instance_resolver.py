from lionweb.api.classifier_instance_resolver import ClassifierInstanceResolver
from lionweb.model import ClassifierInstance


class CompositeClassifierInstanceResolver(ClassifierInstanceResolver):
    """A resolver that delegates to a sequence of resolvers, in order.

    The first resolver able to resolve a given instance ID wins.
    """

    def __init__(self, *classifier_instance_resolvers: ClassifierInstanceResolver):
        self.classifier_instance_resolvers: list[ClassifierInstanceResolver] = list(
            classifier_instance_resolvers
        )

    def add(
        self, classifier_instance_resolver: ClassifierInstanceResolver
    ) -> "CompositeClassifierInstanceResolver":
        """Append a resolver to the chain.

        Args:
            classifier_instance_resolver: The resolver to add.

        Returns:
            CompositeClassifierInstanceResolver: This instance, to allow chaining.
        """
        self.classifier_instance_resolvers.append(classifier_instance_resolver)
        return self

    def resolve(self, instance_id: str) -> ClassifierInstance | None:
        """Resolve the instance ID using the first resolver in the chain that succeeds.

        Args:
            instance_id: The ID of the classifier instance to resolve.

        Returns:
            The resolved classifier instance, or None if no resolver in the chain
            could resolve it.
        """
        for resolver in self.classifier_instance_resolvers:
            instance = resolver.resolve(instance_id)
            if instance is not None:
                return instance
        return None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.classifier_instance_resolvers!r})"

    __str__ = __repr__
