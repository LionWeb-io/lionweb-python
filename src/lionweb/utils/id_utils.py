class IdUtils:

    @staticmethod
    def clean_string(string: str) -> str:
        return string.replace(".", "-")
