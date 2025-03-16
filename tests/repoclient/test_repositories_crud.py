import os

from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.repoclient.repo_client import (RepoClient,
                                                  RepositoryConfiguration)

from .abstract_repo_client_functional_test import \
    AbstractRepoClientFunctionalTest


class RepositoriesCRUD(AbstractRepoClientFunctionalTest):

    def test_list_repositories(self):
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

    def test_delete_repository(self):
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
        repo_client.delete_repository('default')
        self.assertEqual([],repos)
        # All tests should go back to the initial situation
        repo_client.create_repository(RepositoryConfiguration('default', LionWebVersion.V2023_1, False))

    def test_create_repository(self):
        model_repo_url = f"http://localhost:{os.getenv('MODEL_REPO_PORT')}"
        repo_client = RepoClient(
            lionweb_version=LionWebVersion.V2023_1, repo_url=model_repo_url
        )
        repos = repo_client.list_repositories()
        self.assertEqual([RepositoryConfiguration('default', LionWebVersion.V2023_1, False)], repos)
        repo_client.create_repository(RepositoryConfiguration('a', LionWebVersion.V2023_1, False))
        repo_client.create_repository(RepositoryConfiguration('b', LionWebVersion.V2023_1, True))
        repo_client.create_repository(RepositoryConfiguration('c', LionWebVersion.V2024_1, False))
        repo_client.create_repository(RepositoryConfiguration('d', LionWebVersion.V2024_1, True))
        self.assertEqual(
            [
                RepositoryConfiguration('default', LionWebVersion.V2023_1, False),
                RepositoryConfiguration(
                    name="a",
                    lionweb_version=LionWebVersion.V2023_1,
                    history=False,
                ),
                RepositoryConfiguration(
                    name="b",
                    lionweb_version=LionWebVersion.V2023_1,
                    history=True,
                ),
                RepositoryConfiguration(
                    name="c",
                    lionweb_version=LionWebVersion.V2024_1,
                    history=False,
                ),
                RepositoryConfiguration(
                    name="d",
                    lionweb_version=LionWebVersion.V2024_1,
                    history=True,
                )
            ],
            repos,
        )
        # All tests should go back to the initial situation
        repo_client.delete_repository('a')
        repo_client.delete_repository('b')
        repo_client.delete_repository('c')
        repo_client.delete_repository('d')
