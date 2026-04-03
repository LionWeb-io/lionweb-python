JsonObject = dict[str, object]
JsonArray = list[object]
JsonPrimitiveValue = str | int
JsonElement = None | JsonObject | JsonArray | JsonPrimitiveValue
