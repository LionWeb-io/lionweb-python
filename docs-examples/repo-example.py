import uuid
from typing import Optional, List

from lionweb import LionWebVersion
from lionweb.language import Concept, Property, LionCoreBuiltins, Containment, Language
from lionweb.repoclient import RepoClient
from lionweb.model import DynamicNode
from lionweb.repoclient.repo_client import RepositoryConfiguration
from lionweb.utils import root

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

def repo_example():
    # Create the client
    client = RepoClient(lionweb_version=LionWebVersion.V2024_1, repo_url="http://localhost:3005", repository_name="myRepo")
    client.create_repository(RepositoryConfiguration(name='myRepo', lionweb_version=LionWebVersion.V2024_1, history=False))

    # Register the language
    client.serialization().register_language(task_language)

    def task_list_deserializer(classifier, sci, nodes_by_id, property_values) -> TaskList:
        return TaskList(id=sci.id)


    def task_deserializer(classifier, sci, nodes_by_id, property_values) -> Task:
        return Task(id=sci.id, name=property_values[name_property])

    client.serialization().instantiator.register_custom_deserializer(task_list_concept.id, task_list_deserializer)
    client.serialization().instantiator.register_custom_deserializer(task_concept.id, task_deserializer)

    # Create a partition node
    tl1 = TaskList(id="TL1")

    # Create the partition on the server
    client.create_partition(tl1)

    # Create two files
    t1 = Task(name="Do laundry")
    t2 = Task(name="Write documentation for LionWeb Python")

    # Add them to the partition
    tl1.add_task(t1)
    tl1.add_task(t2)

    # Store the model in the repository
    client.store([tl1])

    # Retrieve and check
    retrieved_nodes = client.retrieve(["TL1"])
    assert len(retrieved_nodes) == 3

    retrieved_tl1 = root(retrieved_nodes)
    assert retrieved_tl1.id == 'TL1'

if __name__ == "__main__":
    define_language()
    repo_example()