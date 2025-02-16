from typing import Dict, List

JsonObject = Dict[str, object]
JsonArray = List[object]
JsonPrimitiveValue = str | int
JsonElement = None | JsonObject | JsonArray | JsonPrimitiveValue
