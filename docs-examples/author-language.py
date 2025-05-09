from lionweb.language import Language, Concept, Property, LionCoreBuiltins

from pathlib import Path

from lionweb.serialization import SerializationProvider
from lionweb.utils.language_validator import LanguageValidator

# Define the 'Task' concept
task_concept = Concept(name="Task", key="Task", id="Task-id", abstract=False, partition=False)

# Add a 'name' property
name_property = Property(name="name", key="task-name", id="task-name-id", type=LionCoreBuiltins.get_string())
task_concept.add_feature(name_property)

# Define the language container
task_language = Language(
    name="Task Language",
    key="task",
    id="task-id",
    version="1.0",
)
task_language.add_element(task_concept)

# Validate the language model
res = LanguageValidator().validate(task_language)
if res.has_errors():
    raise ValueError(f"Let's fix these errors: {res.issues}")

# Serialize to JSON
serialization = SerializationProvider.get_standard_json_serialization()
json_output = serialization.serialize_tree_to_json_string(task_language)

# Write to file
Path("task-language.json").write_text(json_output, encoding="utf-8")