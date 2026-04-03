from typing import TYPE_CHECKING, Optional, cast

from lionweb.language.classifier import Classifier
from lionweb.language.interface import Interface


class Annotation(Classifier["Annotation"]):
    if TYPE_CHECKING:
        from lionweb.language.concept import Concept
        from lionweb.language.feature import Feature
        from lionweb.language.interface import Interface
        from lionweb.language.language import Language
        from lionweb.lionweb_version import LionWebVersion

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
            id=id,
        )
        if key:
            self.set_key(key)

    @property
    def annotates(self) -> Classifier | None:
        return cast(Classifier | None, self.get_reference_single_value("annotates"))

    @annotates.setter
    def annotates(self, target: Optional["Classifier"]):
        if target is None:
            self.set_reference_single_value("annotates", None)
        else:
            from lionweb.model.reference_value import ReferenceValue

            self.set_reference_single_value("annotates", ReferenceValue(target, target.get_name()))

    @property
    def extended_annotation(self) -> Optional["Annotation"]:
        return cast(Annotation | None, self.get_reference_single_value("extends"))

    @extended_annotation.setter
    def extended_annotation(self, extended: Optional["Annotation"]):
        if extended is None:
            self.set_reference_single_value("extends", None)
        else:
            from lionweb.model.reference_value import ReferenceValue

            self.set_reference_single_value(
                "extends", ReferenceValue(extended, extended.get_name())
            )

    @property
    def implemented(self) -> list["Interface"]:
        return cast(list[Interface], self.get_reference_multiple_value("implements"))

    def add_implemented_interface(self, iface: "Interface"):
        if iface is None:
            raise ValueError("iface should not be null")
        from lionweb.model.reference_value import ReferenceValue

        self.add_reference_multiple_value("implements", ReferenceValue(iface, iface.get_name()))

    def get_effectively_annotated(self) -> Classifier | None:
        """
        An Annotation extending another annotation should not redefine annotates.
        So the value is effectively inherited from the super annotation.
        """
        annotates = self.annotates
        extended = self.extended_annotation
        if annotates is None and extended is not None:
            return extended.annotates
        return annotates

    def direct_ancestors(self) -> list["Classifier"]:
        direct_ancestors: list[Classifier] = []
        extended = self.extended_annotation
        if extended:
            direct_ancestors.append(extended)
        direct_ancestors.extend(self.implemented)
        return direct_ancestors

    def inherited_features(self) -> list["Feature"]:
        from lionweb.language.feature import Feature

        result: list[Feature] = []
        extended = self.extended_annotation
        if extended:
            self.combine_features(result, extended.all_features())
        for super_interface in self.implemented:
            self.combine_features(result, super_interface.all_features())
        return result

    def get_classifier(self) -> "Concept":
        from lionweb.self.lioncore import LionCore

        return LionCore.get_annotation(self.get_lionweb_version())
