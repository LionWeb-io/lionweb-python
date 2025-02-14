import unittest

from lionwebpython.language.annotation import Annotation
from lionwebpython.language.concept import Concept
from lionwebpython.language.interface import Interface


class ClassifierAncestorsTest(unittest.TestCase):

    def test_concept(self):
        a = Concept("A")
        b = Concept("b")
        i = Interface("i")
        j = Interface("j")
        k = Interface("k")
        myInterf = Interface("l")

        a.set_extended_concept(b)
        a.add_implemented_interface(i)
        a.add_implemented_interface(j)
        i.add_extended_interface(k)
        b.add_implemented_interface(myInterf)
        k.add_extended_interface(myInterf)

        self.assertEqual(set([b, i, j]), set(a.direct_ancestors()))
        self.assertEqual(set([b, i, j, k, myInterf]), set(a.all_ancestors()))

    def test_annotation(self):
        a = Annotation()
        a.set_name("A")
        b = Annotation()
        b.set_name("b")
        i = Interface("i")
        j = Interface("j")
        k = Interface("k")
        myInterf = Interface("l")

        a.set_extended_annotation(b)
        a.add_implemented_interface(i)
        a.add_implemented_interface(j)
        i.add_extended_interface(k)
        b.add_implemented_interface(myInterf)
        k.add_extended_interface(myInterf)

        self.assertEqual(set([b, i, j]), set(a.direct_ancestors()))
        self.assertEqual(set([b, i, j, k, myInterf]), set(a.all_ancestors()))

    def test_iface(self):
        i = Interface("i")
        j = Interface("j")
        k = Interface("k")
        myInterf = Interface("l")

        i.add_extended_interface(j)
        i.add_extended_interface(k)
        k.add_extended_interface(myInterf)
        k
