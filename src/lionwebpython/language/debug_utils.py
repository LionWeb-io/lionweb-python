class DebugUtils:

    @staticmethod
    def qualified_name(namespaced_entity) -> str:
        """
        This variant of qualified name can be obtained also for invalid states. This is intended to be
        used in methods which should not throw exceptions, like toString methods.
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
