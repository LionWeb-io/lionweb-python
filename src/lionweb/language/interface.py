import itertools
from typing import TYPE_CHECKING, Optional

from lionweb.language.classifier import Classifier


class Interface(Classifier["Interface"]):
    """A classifier that declares features to be implemented/inherited by concepts and other
    interfaces, without being directly instantiable."""

    if TYPE_CHECKING:
        from lionweb.language.concept import Concept
        from lionweb.language.feature import Feature
        from lionweb.language.language import Language
        from lionweb.lionweb_version import LionWebVersion
        from lionweb.self.lioncore import LionCore

    def __init__(
        self,
        lion_web_version: Optional["LionWebVersion"] = None,
        language: Optional["Language"] = None,
        name: str | None = None,
        id: str | None = None,
        key: str | None = None,
    ):
        from lionweb.lionweb_version import LionWebVersion

        super().__init__(
            lion_web_version=lion_web_version or LionWebVersion.current_version(),
            language=language,
            name=name,
        )
        if id:
            self.set_id(id)
        if key:
            self.set_key(key)

    def get_extended_interfaces(self) -> list["Interface"]:
        return self.get_reference_multiple_value("extends")

    @property
    def extended_interfaces(self) -> list["Interface"]:
        return self.get_extended_interfaces()

    def add_extended_interface(self, extended_interface: "Interface") -> None:
        """Add an interface to the list of interfaces this interface extends.

        Args:
            extended_interface: The interface to extend.

        Raises:
            ValueError: If ``extended_interface`` is ``None``.
        """
        if not extended_interface:
            raise ValueError("extended_interface should not be null")

        from lionweb.model.classifier_instance_utils import reference_to

        self.add_reference_multiple_value("extends", reference_to(extended_interface))

    def inherited_features(self) -> list["Feature"]:
        from lionweb.language.feature import Feature

        result: list[Feature] = []
        for super_interface in self.all_ancestors():
            self.combine_features(result, super_interface.all_features())
        return result

    def get_classifier(self) -> "Concept":
        from lionweb.self.lioncore import LionCore

        return LionCore.get_interface(self.get_lionweb_version())

    def direct_ancestors(self) -> list[Classifier]:
        return list(itertools.chain(self.get_extended_interfaces()))

    def all_extended_interfaces(self) -> set["Interface"]:
        """Compute the transitive closure of all interfaces extended by this interface (cycle-safe).

        Returns:
            set[Interface]: All directly and indirectly extended interfaces.
        """
        to_avoid = {self}
        return self._all_extended_interfaces_helper(to_avoid)

    def _all_extended_interfaces_helper(self, to_avoid: set["Interface"]) -> set["Interface"]:
        interfaces = set()
        to_avoid.add(self)
        for ei in self.get_extended_interfaces():
            if ei not in interfaces:
                interfaces.add(ei)
            if ei not in to_avoid:
                interfaces.update(ei._all_extended_interfaces_helper(to_avoid))
        return interfaces

    def __repr__(self) -> str:
        return f"Interface({self.get_name()})"
