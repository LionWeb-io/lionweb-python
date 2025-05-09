---
sidebar_position: 42
---

# Creating and Working with Nodes in LionWeb

LionWeb provides a flexible and language-agnostic model for working with models (or trees, or ASTs: let's consider these as synonyms in this context). 

The main component is the **Node**.

When working with LionWeb nodes in Python, there are **two complementary approaches** depending on your needs:

1. **Homogeneous nodes**, using generic, universal APIs which work with all form of nodes. When choosing this approach, we may want to consider `DynamicNode`.
2. **Heterogeneous nodes**, using language-specific, statically-typed Python classes, defined for a certain LionWeb language and just that one.

## The Core Abstraction: `Node`

At the heart of LionWeb is the `Node` interface. Implementing it guarantees:

- Serialization and deserialization
- Compatibility with the LionWeb Repository
- Introspection through classifiers and features
- Tool support (e.g., editors, model processors)

By relying on this interface, LionWeb tooling can process, manipulate, and analyze any conforming node in a uniform manner.

## Option 1: Homogeneous Nodes

This approach is ideal for **generic tools** and **runtime interoperability**. The key class here is `DynamicNode`.

### When to Use

- You receive nodes from external systems or clients
- You want to handle **unknown or dynamic languages**
- You’re building **generic tools** (e.g., validators, browsers)

### How it Works

`DynamicNode` implements `Node` and stores features dynamically. You can query and manipulate the node’s structure by name.

### Example

```python
from lionweb.language import Language, Concept, Property, Containment
from lionweb.model import DynamicNode
from lionweb.language import LionCoreBuiltins
from lionweb.utils.node_tree_validator import NodeTreeValidator

# === Define the Language ===

# Define the 'TaskList' concept
task_list_concept = Concept(
    name="TaskList", key="TaskList", id="TaskList-id", abstract=False, partition=True
)

# Define the 'Task' concept
task_concept = Concept(
    name="Task", key="Task", id="Task-id", abstract=False, partition=False
)

# Add a 'tasks' containment
tasks_containment = Containment(
    name="tasks",
    key="TasksList-tasks",
    id="TasksList-tasks-id",
    type=task_concept,
    multiple=True,
    optional=False,
)
task_list_concept.add_feature(tasks_containment)

# Add a 'name' property
name_property = Property(
    name="name", key="task-name", id="task-name-id", type=LionCoreBuiltins.get_string()
)
task_concept.add_feature(name_property)

# Define the language container
task_language = Language(
    name="Task Language",
    key="task",
    id="task-id",
    version="1.0"
)
task_language.add_element(task_list_concept)
task_language.add_element(task_concept)

# === Use DynamicNode to Build a Model ===

# Create root node (a TaskList)
errands = DynamicNode(id="errands", concept=task_list_concept)

# Create first Task node
task1 = DynamicNode(id="task1-id", concept=task_concept)
task1.set_property_value(property=name_property, value="My Task #1")
errands.add_child(tasks_containment, task1)

# Create second Task node
task2 = DynamicNode(id="task2-id", concept=task_concept)
task2.set_property_value(name_property, "My Task #2")
errands.add_child(tasks_containment, task2)

# Validate the model tree
result = NodeTreeValidator().validate(errands)
if result.has_errors():
    raise ValueError(f"The tree is invalid: {result}")

# Access the model using direct containment
tasks = errands.get_children(tasks_containment)
print(f"Tasks found: {len(tasks)}")
for task in tasks:
    print(f" - {task.get_property_value(name_property)}")

# Access the model using name-based utilities
tasks_again = errands.get_children("tasks")
print(f"Tasks found again: {len(tasks_again)}")
for task in tasks_again:
    print(f" - {task.get_property_value('name')}")
```

### Evaluation

- No static typing
- No compile-time safety
- No code completion or type checking
- Work out of the box, without the need to write any code for each language

If you misspell `"name"` or access a non-existent feature, you’ll get a runtime exception.

## Option 2: Heterogeneous Nodes

This approach is recommended when building **interpreters**, **compilers**, or other tools for a **specific language**.

You define a Python class for each concept, typically:

- Implementing the `Node` interface
- Optionally extending `DynamicNode` for convenience

### But how can you define these classes?

Of course, you can do that in the good old way: writing the code yourself.

Or you can define a code generator which, given a language, produce the corresponding classes. This may also be a feature we eventually implement in LionWeb Python.

### When to Use

- You are building tooling for a specific DSL or language
- You want type-safe code with IDE support
- You require structured, validated access to features

### Example

```python
import uuid
from typing import List, cast

from lionweb.language import Language, Concept, Property, Containment
from lionweb.model import DynamicNode
from lionweb.language import LionCoreBuiltins
from lionweb.utils.node_tree_validator import NodeTreeValidator


# === Define the Language ===

# Global elements
task_list_concept: Concept
task_concept: Concept
name_property: Property
tasks_containment: Containment
task_language: Language


def define_language():
    global task_list_concept, task_concept, name_property, tasks_containment, task_language

    # Define the 'TaskList' concept
    task_list_concept = Concept(
        name="TaskList", key="TaskList", id="TaskList-id", abstract=False, partition=True
    )

    # Define the 'Task' concept
    task_concept = Concept(
        name="Task", key="Task", id="Task-id", abstract=False, partition=False
    )

    # Add a 'tasks' containment
    tasks_containment = Containment(
        name="tasks",
        key="TasksList-tasks",
        id="TasksList-tasks-id",
        type=task_concept,
        multiple=True,
        optional=False,
    )
    task_list_concept.add_feature(tasks_containment)

    # Add a 'name' property
    name_property = Property(
        name="name", key="task-name", id="task-name-id", type=LionCoreBuiltins.get_string()
    )
    task_concept.add_feature(name_property)

    # Define the language container
    task_language = Language(
        name="Task Language",
        key="task",
        id="task-id",
        version="1.0"
    )
    task_language.add_element(task_list_concept)
    task_language.add_element(task_concept)


# === Define specific DynamicNode subclasses ===

class Task(DynamicNode):
    def __init__(self, name: str):
        super().__init__(str(uuid.uuid4()), task_concept)
        self.set_name(name)

    def set_name(self, name: str):
        self.set_property_value(name_property, name)

    def get_name(self) -> str:
        return self.get_property_value(name_property)


class TaskList(DynamicNode):
    def __init__(self):
        super().__init__(str(uuid.uuid4()), task_list_concept)

    def add_task(self, task: Task):
        self.add_child(tasks_containment, task)

    def get_tasks(self) -> List[Task]:
        return self.get_children(tasks_containment)


# === Main usage function ===

def use_specific_classes():
    define_language()

    errands = TaskList()

    task1 = Task("My Task #1")
    errands.add_task(task1)

    task2 = Task("My Task #2")
    errands.add_task(task2)

    # Validate
    result = NodeTreeValidator().validate(errands)
    if result.has_errors():
        raise ValueError(f"The tree is invalid: {result}")

    # Access
    tasks = errands.get_tasks()
    print(f"Tasks found: {len(tasks)}")
    for task in tasks:
        print(f" - {task.get_name()}")


# === Entry Point ===

if __name__ == "__main__":
    use_specific_classes()
```

### Evaluation

- Full IDE support (auto-completion, navigation)
- Catch errors at compile time
- Clear API for collaborators
- Require extra work for defining the classes

## Suggested approach

- Use `DynamicNode` in **model editors**, **importers**, **migrators**
- Use custom classes (like `PersonNode`) in **interpreters**, **generators**, **type checkers**

## Interoperability

Both approaches can co-exist. For example, you might parse a file into `DynamicNode` objects and then convert them into typed classes using a factory or builder.
