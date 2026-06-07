class DebugUtils:
    """Helper utilities for producing debug-friendly string representations."""

    @staticmethod
    def qualified_name(namespaced_entity) -> str:
        """Compute a best-effort qualified name for a namespaced entity.

        This variant of qualified name can be obtained also for invalid states. This is intended to be
        used in methods which should not throw exceptions, like toString methods.

        Args:
            namespaced_entity: The entity (typically a ``NamespacedEntity``) to describe.

        Returns:
            str: A qualified name such as ``"<unnamed language>.<unnamed>"`` falling back to
            placeholder text when the container or name is missing.
        """
        qualifier = "<no language>"
        if namespaced_entity.get_container() is not None:
            if namespaced_entity.get_container().namespace_qualifier() is not None:
                qualifier = namespaced_entity.get_container().namespace_qualifier()
            else:
                qualifier = "<unnamed language>"

        qualified = "<unnamed>"
        if namespaced_entity.get_name() is not None:
            qualified = namespaced_entity.get_name()

        return f"{qualifier}.{qualified}"
