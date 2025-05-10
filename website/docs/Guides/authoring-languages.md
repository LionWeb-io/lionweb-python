---
sidebar_position: 41
---

# Authoring Languages for LionWeb

LionWeb is an open initiative to enable **interoperability among language engineering tools**. 

Therefore, typically one would:
* Use one of the tools compatible with LionWeb to author a language
* Export the language into LionWeb format and import it in other tools

Alternatively, a language can also be defined programmatically using the API provided by LionWeb Python.

## Using LionWeb-compatible tools to author languages

In most real-world use cases, **language definitions (or metamodels)** are created using **dedicated language workbenches or modeling tools**. These tools provide expressive, user-friendly environments to author, maintain, and evolve languages.

You may want to consider

- [**JetBrains MPS**](https://www.jetbrains.com/mps/): A powerful projectional editor with LionWeb export support provided through [LionWeb MPS](http://github.com/lionweb-io/lionweb-mps).
- [**Freon**](https://www.freon4dsl.dev/): A lightweight web-based projectional editor, with support for LionWeb provided through [LionWeb-Freon-M3](https://github.com/LionWeb-io/lionweb-freon-m3).
- [**StarLasu**](https://starlasu.strumenta.com/): A cross-platform framework for language engineering framework developed by [Strumenta](https://strumenta.com).

These tools allow engineers to create languages using their built-in mechanisms and then **export them to LionWeb-compatible formats**. Once exported, these languages can be:

- Used in other LionWeb-aware tools.
- Serialized to formats like **JSON**, **FlatBuffer**, or **BroadBuffer**.
- Re-imported across the ecosystem.

This workflow maximizes **interoperability and reuse**, allowing language definitions to move seamlessly across platforms.

---

## Authoring Languages Programmatically

While most users rely on external tools, **it is also possible to author languages programmatically** using LionWeb-Python.

Using the API in the `core` module, you can define metamodels directly in Python code. This gives you the flexibility to:

- Build metamodels dynamically.
- Serialize and persist them.
- Use them in Python libraries and programs.
- Export them to LionWeb formats for use elsewhere.

### Supported Serialization Formats

The LionWeb Python implementation supports serialization in **JSON** (standard and human-readable).
As of now, it does not support **ProtoBuf** and **FlatBuffers** (compact binary format). If you want support
for them to be added please feel free to reach out and let us know.

---

## Example: Defining a Language Programmatically

The following example shows how to define a minimal language with a single concept `Task` that has a `name` property.

```python
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
serialization = SerializationProvider.create_standard_json_serialization()
json_output = serialization.serialize_tree_to_json_string(task_language)

# Write to file
Path("task-language.json").write_text(json_output, encoding="utf-8")
```
