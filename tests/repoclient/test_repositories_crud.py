import os

from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.repoclient.repo_client import (RepoClient,
                                                  RepositoryConfiguration)

from .abstract_repo_client_functional_test import \
    AbstractRepoClientFunctionalTest


class RepositoriesCRUD(AbstractRepoClientFunctionalTest):

    def test_list_repositories(self):
        """Test retrieving data from the model repository."""
        # model_repo_url = f"http://localhost:{self.model_repo_port}"
        print(f"[DEBUG] Environment MODEL_REPO_PORT = {os.getenv('MODEL_REPO_PORT')}")
        model_repo_url = f"http://localhost:{os.getenv('MODEL_REPO_PORT')}"
        repo_client = RepoClient(
            lionweb_version=LionWebVersion.V2023_1, repo_url=model_repo_url
        )
        repos = repo_client.list_repositories()
        self.assertEqual(
            [
                RepositoryConfiguration(
                    name="default",
                    lionweb_version=LionWebVersion.V2023_1,
                    history=False,
                )
            ],
            repos,
        )

    #
    #
    # def test_post_data(self):
    #     """Test sending data to the model repository."""
    #     payload = {"name": "TestItem"}
    #     response = requests.post(f"{MODEL_REPO_URL}/api/data", json=payload)
    #     assert response.status_code == 201
    #     assert response.json()["name"] == "TestItem"
