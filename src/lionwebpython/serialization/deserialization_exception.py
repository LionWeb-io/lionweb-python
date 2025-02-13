class DeserializationException(RuntimeError):

    def __init__(self, message: str, e: "DeserializationException"):
        if e is None:
            super().__init__("Problem during deserialization: " + message)
        else:
            super().__init__("Problem during deserialization: " + message, e)
            self.__cause__ = e
