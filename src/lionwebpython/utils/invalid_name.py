class InvalidName(RuntimeError):

    def __init__(self, name_type: str, value: str):
        super().__init__(
            "The given name is not a valid " + name_type + ". Value: '" + value + "'"
        )
