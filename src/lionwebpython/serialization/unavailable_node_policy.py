from enum import Enum


class UnavailableNodePolicy(Enum):
    """
    When deserializing a tree, we either extract an entire partition (and perhaps all the referred
    partitions) or we will get references to nodes (for example, parents or ancestors) outside of the
    scope of the tree extracted. This policy specifies what we do with such references.
    """

    NULL_REFERENCES = "NULL_REFERENCES"
    THROW_ERROR = "THROW_ERROR"
    PROXY_NODES = "PROXY_NODES"
