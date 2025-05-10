import uuid
from typing import List, Optional

from lionweb.language import Language, Concept, Property, Containment, LionCoreBuiltins
from lionweb.model import DynamicNode
from lionweb.serialization import create_standard_json_serialization, InstantiationError
from lionweb.utils import root
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
    def __init__(self, name: str, id: Optional[str] = None):
        super().__init__(id or str(uuid.uuid4()), task_concept)
        self.set_name(name)

    def set_name(self, name: str):
        self.set_property_value(name_property, name)

    def get_name(self) -> str:
        return self.get_property_value(name_property)


class TaskList(DynamicNode):
    def __init__(self, id:Optional[str] = None):
        super().__init__(id or str(uuid.uuid4()), task_list_concept)

    def add_task(self, task: Task):
        self.add_child(tasks_containment, task)

    def get_tasks(self) -> List[Task]:
        return self.get_children(tasks_containment)

# === Main logic ===

def create_task_list() -> TaskList:
    define_language()

    errands = TaskList()
    errands.add_task(Task("My Task #1"))
    errands.add_task(Task("My Task #2"))

    result = NodeTreeValidator().validate(errands)
    if result.has_errors():
        raise ValueError(f"The tree is invalid: {result}")

    return errands


if __name__ == "__main__":
    task_list = create_task_list()
    serialization = create_standard_json_serialization()

    # === Serialize
    serialized = serialization.serialize_tree_to_json_string(task_list)
    print("== Tasks list ==")
    print(serialized)
    print()

    # === Attempt deserialization without dynamic mode
    try:
        serialization.deserialize_string_to_nodes(serialized)
        raise RuntimeError("We expect an exception")
    except InstantiationError as e:
        print("Expected error:", e)

    # === First deserialization with dynamic nodes
    serialization.enable_dynamic_nodes()
    deserialized1 = root(serialization.deserialize_string_to_nodes(serialized))
    print("First deserialization - Deserialized as", type(deserialized1).__name__)
    if type(deserialized1) is not DynamicNode:
        raise RuntimeError("Deserialized object should be a DynamicNode")


    # === Register custom deserializers
    def task_list_deserializer(classifier, sci, nodes_by_id, property_values) -> TaskList:
        return TaskList(id=sci.id)


    def task_deserializer(classifier, sci, nodes_by_id, property_values) -> Task:
        return Task(id=sci.id, name=property_values[name_property])


    serialization.instantiator.register_custom_deserializer(task_list_concept.id, task_list_deserializer)
    serialization.instantiator.register_custom_deserializer(task_concept.id, task_deserializer)

    deserialized2 = root(serialization.deserialize_string_to_nodes(serialized))
    print("Second deserialization - Deserialized as", type(deserialized2).__name__)
    if type(deserialized2) is not TaskList:
        raise RuntimeError(f"Deserialized object should be a TaskList while it is {type(deserialized2)}")