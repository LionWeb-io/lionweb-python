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