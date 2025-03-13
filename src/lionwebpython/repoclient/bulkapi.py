from typing import Optional, List

import requests

from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.model import ClassifierInstance
from lionwebpython.model.impl.dynamic_node import DynamicNode
from lionwebpython.model.node import Node
from lionwebpython.serialization.serialization_provider import SerializationProvider


class RepoClient:

    def __init__(self, lionweb_version=LionWebVersion.current_version(), repo_url="http://localhost:3005", client_id = "lwpython", repository_name:Optional[str]="default"):
        self._lionweb_version = lionweb_version
        self._repo_url = repo_url
        self._client_id = client_id
        self._repository_name = repository_name

    def create_partitions(self, nodes: List['Node']):
        for n in nodes:
            if len(n.get_children(containment=None))>0:
                raise ValueError("Cannot store a node with children as a new partition")

        url = f"{self._repo_url}/bulk/createPartitions"
        headers = {"Content-Type": "application/json"}
        query_params = {"repository": self._repository_name, "clientId": self._client_id}
        data = SerializationProvider.get_standard_json_serialization(
            self._lionweb_version).serialize_trees_to_json_element(nodes)
        response = requests.post(url, params=query_params, json=data, headers=headers)
        if response.status_code != 200:
            raise ValueError("Error:", response.status_code, response.text)


    def store(self, nodes: List['ClassifierInstance']):
        url = f"{self._repo_url}/bulk/store"
        headers = {"Content-Type": "application/json"}
        query_params = {"repository": self._repository_name, "clientId": self._client_id}
        data = SerializationProvider.get_standard_json_serialization(self._lionweb_version).serialize_trees_to_json_element(nodes)
        response = requests.post(url, params=query_params, json=data, headers=headers)
        if response.status_code != 200:
            raise ValueError("Error:", response.status_code, response.text)


    def retrieve(self, ids:List[str], depth_limit=None):
        url = f"{self._repo_url}/bulk/retrieve"
        headers = {"Content-Type": "application/json"}
        query_params = {"repository": self._repository_name, "clientId": self._client_id}
        response = requests.post(url, params=query_params, json={"ids":ids}, headers=headers)
        # Check response
        if response.status_code == 200:
            data = response.json()
            print(data)
            nodes = SerializationProvider.get_standard_json_serialization(self._lionweb_version).deserialize_json_to_nodes(data['chunk'])
            return nodes
        else:
            raise ValueError("Error:", response.status_code, response.text)

# client = RepoClient(lionweb_version=LionWebVersion.V2023_1, repository_name="alt")
# path = '/Users/ftomassetti/repos/lionweb-java/core/src/test/resources/properties-example/starlasu-corrected.lmm.json'
# with open(path, "r", encoding="utf-8") as file:
#     content = file.read()
# nodes = SerializationProvider.get_standard_json_serialization(LionWebVersion.V2023_1).deserialize_string_to_nodes(content)
# for n in nodes:
#     print(f"node {n.get_id()}")
#     for p in n.get_classifier().all_properties():
#         print(f" - {p.get_name()}={n.get_property_value(property=p)}")
# root = nodes[0]
# simplified_root = DynamicNode(root.id, root.get_classifier())
# client.create_partitions([simplified_root])
# print("PARTITION CREATED")
# client.store(nodes)
# print("STORED")
# nodes = client.retrieve(["com-strumenta-StarLasu"])
# for n in nodes:
#     print(f"node {n.get_id()}")
#     for p in n.get_classifier().all_properties():
#         print(f" - {p.get_name()}={n.get_property_value(property=p)}")