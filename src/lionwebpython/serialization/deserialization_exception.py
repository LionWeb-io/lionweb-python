from typing import Optional


class DeserializationException(RuntimeError):

    def __init__(self, message: str, e: Optional["DeserializationException"] = None):
        if e is None:
            super().__init__("Problem during deserialization: " + message)
        else:
            super().__init__("Problem during deserialization: " + message, e)
            self.__cause__ = e
