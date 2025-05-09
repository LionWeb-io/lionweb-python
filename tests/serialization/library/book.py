from typing import Optional, cast

from serialization.library.writer import Writer

from lionweb.language.concept import Concept
from lionweb.model.classifier_instance_utils import (
    get_only_reference_value_by_reference_name, get_property_value_by_name)
from lionweb.model.impl.dynamic_node import DynamicNode
from lionweb.model.reference_value import ReferenceValue


class Book(DynamicNode):
    def __init__(self, id: str, title: str = None, author: "Writer" = None):
        from serialization.library.library_language import LibraryLanguage

        super().__init__(id, LibraryLanguage.BOOK)
        if title is not None:
            self.title = title
        if author is not None:
            self.author = author

    @property
    def title(self) -> str:
        return cast(str, get_property_value_by_name(self, "title"))

    @title.setter
    def title(self, value: str):
        property_ = self.get_classifier().get_property_by_name("title")
        self.set_property_value(property=property_, value=value)

    @property
    def pages(self) -> int:
        return cast(int, get_property_value_by_name(self, "pages"))

    @pages.setter
    def pages(self, value: int):
        property_ = self.get_classifier().get_property_by_name("pages")
        self.set_property_value(property=property_, value=value)

    @property
    def author(self) -> Optional["Writer"]:
        res = get_only_reference_value_by_reference_name(self, "author")
        if res:
            return cast(Writer, res.referred)
        else:
            return None

    @author.setter
    def author(self, author: "Writer"):
        reference = self.get_classifier().get_reference_by_name("author")
        if self.author:
            self.remove_reference_value_by_index(reference, 0)
        self.add_reference_value(reference, ReferenceValue(author, author.get_name()))

    def get_classifier(self) -> Concept:
        from serialization.library.library_language import LibraryLanguage

        return LibraryLanguage.BOOK
