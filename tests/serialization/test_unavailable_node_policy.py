import unittest

from lionwebpython.serialization.unavailable_node_policy import \
    UnavailableNodePolicy


class TestUnavailableNodePolicy(unittest.TestCase):

    def test_enum_values(self):
        assert UnavailableNodePolicy.NULL_REFERENCES.value == "NULL_REFERENCES"
        assert UnavailableNodePolicy.THROW_ERROR.value == "THROW_ERROR"
        assert UnavailableNodePolicy.PROXY_NODES.value == "PROXY_NODES"


if __name__ == "__main__":
    unittest.main()
