class UnresolvedClassifierInstanceException(RuntimeError):

    def __init__(self, instance_id: str):
        super().__init__(f"Unable to resolve classifier instance with ID={instance_id}")
        self._instance_id = instance_id

    @property
    def instance_id(self) -> str:
        return self._instance_id
