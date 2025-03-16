import requests

from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.repoclient.repo_client import RepoClient
from .abstract_repo_client_functional_test import AbstractRepoClientFunctionalTest


class RepositoriesCRUD(AbstractRepoClientFunctionalTest):

    def test_list_repositories(self):
        """Test retrieving data from the model repository."""
        model_repo_url = f"http://localhost:{self.model_repo_port}"
        repo_client = RepoClient(lionweb_version=LionWebVersion.V2023_1)
        response = requests.get(f"{model_repo_url}/api/data")
        assert response.status_code == 200
        assert "result" in response.json()
    #
    #
    # def test_post_data(self):
    #     """Test sending data to the model repository."""
    #     payload = {"name": "TestItem"}
    #     response = requests.post(f"{MODEL_REPO_URL}/api/data", json=payload)
    #     assert response.status_code == 201
    #     assert response.json()["name"] == "TestItem"