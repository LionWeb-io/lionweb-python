class UnresolvedClassifierInstanceException(RuntimeError):

    def __init__(self, instance_id: str):
        super().__init__("Unable to resolve classifier instance with ID=" + instance_id)
        self._instance_id = instance_id

    def get_instance_id(self) -> str:
        return self._instance_id
