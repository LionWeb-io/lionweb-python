from typing import Dict, List, Union

JsonObject = Dict[str, object]
JsonArray = List[object]
JsonPrimitiveValue = Union[str, int]
JsonElement = Union[None, JsonObject, JsonArray, JsonPrimitiveValue]
