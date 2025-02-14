from lionwebpython.language.ikeyed import IKeyed
from lionwebpython.language.namespace_provider import NamespaceProvider
from lionwebpython.model.impl.m3node import M3Node


class Language(M3Node["Language"], NamespaceProvider, IKeyed["Language"]):
    def add_element(self, self1):
        raise ValueError("NOT YET IMPLEMENTED")
