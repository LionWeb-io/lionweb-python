from typing import Optional


class UsedLanguage:
    """
    The pair Language Key and Language Version identify a specific version of a language.
    Corresponds to the Java class 'UsedLanguage'.
    """

    def __init__(self, key: Optional[str] = None, version: Optional[str] = None):
        self.key = key
        self.version = version

    @staticmethod
    def from_language(language):
        """
        Create a UsedLanguage instance from a Language object.

        Args:
            language: An object with `key` and `version` attributes.

        Returns:
            UsedLanguage: An instance of UsedLanguage.

        Raises:
            ValueError: If language or its attributes are None.
        """
        if language is None:
            raise ValueError("Language parameter should not be null")
        if language.version is None:
            raise ValueError("Language version should not be null")
        return UsedLanguage(language.key, language.version)

    @staticmethod
    def from_meta_pointer(meta_pointer):
        """
        Create a UsedLanguage instance from a MetaPointer object.

        Args:
            meta_pointer: An object with `language` and `version` attributes.

        Returns:
            UsedLanguage: An instance of UsedLanguage.

        Raises:
            ValueError: If meta_pointer or its attributes are None.
        """
        if meta_pointer is None:
            raise ValueError("meta_pointer parameter should not be null")
        if meta_pointer.language is None:
            raise ValueError("meta_pointer language should not be null")
        if meta_pointer.version is None:
            raise ValueError("meta_pointer version should not be null")
        return UsedLanguage(meta_pointer.language, meta_pointer.version)

    def get_key(self) -> Optional[str]:
        return self.key

    def set_key(self, key: str):
        self.key = key

    def get_version(self) -> Optional[str]:
        return self.version

    def set_version(self, version: str):
        self.version = version

    def __eq__(self, other):
        if not isinstance(other, UsedLanguage):
            return False
        return self.key == other.key and self.version == other.version

    def __hash__(self):
        return hash((self.key, self.version))

    def __str__(self):
        return f"UsedLanguage{{key='{self.key}', version='{self.version}'}}"
