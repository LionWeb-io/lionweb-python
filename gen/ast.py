from abc import ABC
from dataclasses import dataclass
from typing import Optional, cast
from enum import Enum

from lionweb.model.classifier_instance_utils import ClassifierInstanceUtils
from lionweb.model.impl.dynamic_node import DynamicNode
from language import get_language, get_book, get_library, get_writer, get_guidebookwriter, get_specialistbookwriter


class Book(DynamicNode):

    def __init__(self, id: str):
        super().__init__(id, get_book())

    @property
    def title(self) ->str:
        return cast(str, ClassifierInstanceUtils.get_property_value_by_name
            (self, 'title'))

    @title.setter
    def title(self, value: str):
        property_ = self.get_classifier().get_property_by_name('title')
        self.set_property_value(property=property_, value=value)

    @property
    def pages(self) ->str:
        return cast(str, ClassifierInstanceUtils.get_property_value_by_name
            (self, 'pages'))

    @pages.setter
    def pages(self, value: str):
        property_ = self.get_classifier().get_property_by_name('pages')
        self.set_property_value(property=property_, value=value)

    @property
    def author(self) ->str:
        return cast(str, ClassifierInstanceUtils.get_property_value_by_name
            (self, 'author'))

    @author.setter
    def author(self, value: str):
        property_ = self.get_classifier().get_property_by_name('author')
        self.set_property_value(property=property_, value=value)


class Library(DynamicNode):

    def __init__(self, id: str):
        super().__init__(id, get_library())

    @property
    def name(self) ->str:
        return cast(str, ClassifierInstanceUtils.get_property_value_by_name
            (self, 'name'))

    @name.setter
    def name(self, value: str):
        property_ = self.get_classifier().get_property_by_name('name')
        self.set_property_value(property=property_, value=value)

    @property
    def books(self) ->str:
        return cast(str, ClassifierInstanceUtils.get_property_value_by_name
            (self, 'books'))

    @books.setter
    def books(self, value: str):
        property_ = self.get_classifier().get_property_by_name('books')
        self.set_property_value(property=property_, value=value)


class Writer(DynamicNode):

    def __init__(self, id: str):
        super().__init__(id, get_writer())

    @property
    def name(self) ->str:
        return cast(str, ClassifierInstanceUtils.get_property_value_by_name
            (self, 'name'))

    @name.setter
    def name(self, value: str):
        property_ = self.get_classifier().get_property_by_name('name')
        self.set_property_value(property=property_, value=value)


class GuideBookWriter(DynamicNode):

    def __init__(self, id: str):
        super().__init__(id, get_guidebookwriter())

    @property
    def countries(self) ->str:
        return cast(str, ClassifierInstanceUtils.get_property_value_by_name
            (self, 'countries'))

    @countries.setter
    def countries(self, value: str):
        property_ = self.get_classifier().get_property_by_name('countries')
        self.set_property_value(property=property_, value=value)


class SpecialistBookWriter(DynamicNode):

    def __init__(self, id: str):
        super().__init__(id, get_specialistbookwriter())

    @property
    def subject(self) ->str:
        return cast(str, ClassifierInstanceUtils.get_property_value_by_name
            (self, 'subject'))

    @subject.setter
    def subject(self, value: str):
        property_ = self.get_classifier().get_property_by_name('subject')
        self.set_property_value(property=property_, value=value)
