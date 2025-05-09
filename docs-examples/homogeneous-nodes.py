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
