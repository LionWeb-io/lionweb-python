from serialization.library.writer import Writer

from lionwebpython.language.concept import Concept
from lionwebpython.model.classifier_instance_utils import \
    ClassifierInstanceUtils
from lionwebpython.model.impl.dynamic_node import DynamicNode
from lionwebpython.model.reference_value import ReferenceValue


class Book(DynamicNode):
    def __init__(self, id: str, title: str = None, author: "Writer" = None):
        from serialization.library.library_language import LibraryLanguage

        super().__init__(id, LibraryLanguage.BOOK)
        if title is not None:
            self.set_title(title)
        if author is not None:
            self.set_author(author)

    def set_title(self, title: str):
        property_ = self.get_classifier().get_property_by_name("title")
        self.set_property_value(property=property_, value=title)

    def set_pages(self, pages: int) -> "Book":
        property_ = self.get_classifier().get_property_by_name("pages")
        self.set_property_value(property=property_, value=pages)
        return self

    def get_title(self) -> str:
        return ClassifierInstanceUtils.get_property_value_by_name(self, "title")

    def set_author(self, author: "Writer"):
        reference = self.get_classifier().get_reference_by_name("author")
        self.add_reference_value(reference, ReferenceValue(author, author.get_name()))

    def get_classifier(self) -> Concept:
        from serialization.library.library_language import LibraryLanguage

        return LibraryLanguage.BOOK
