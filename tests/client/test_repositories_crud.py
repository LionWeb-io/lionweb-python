import os

from lionweb.client.client import Client, RepositoryConfiguration
from lionweb.lionweb_version import LionWebVersion

from .abstract_client_functional_test import AbstractClientFunctionalTest


class RepositoriesCRUD(AbstractClientFunctionalTest):

    def test_list_repositories(self):
        server_url = f"http://localhost:{os.getenv('SERVER_PORT')}"
        repo_client = Client(
            lionweb_version=LionWebVersion.V2023_1, server_url=server_url
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
        server_url = f"http://localhost:{os.getenv('SERVER_PORT')}"
        repo_client = Client(
            lionweb_version=LionWebVersion.V2023_1, server_url=server_url
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
        repo_client.delete_repository("default")
        repos = repo_client.list_repositories()
        self.assertEqual([], repos)

        # All tests should go back to the initial situation
        repo_client.create_repository(
            RepositoryConfiguration(
                name="default", lionweb_version=LionWebVersion.V2023_1, history=False
            )
        )

    def test_create_repository(self):
        server_url = f"http://localhost:{os.getenv('SERVER_PORT')}"
        repo_client = Client(
            lionweb_version=LionWebVersion.V2023_1, server_url=server_url
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
        repo_client.create_repository(
            RepositoryConfiguration(
                name="a", lionweb_version=LionWebVersion.V2023_1, history=False
            )
        )
        repo_client.create_repository(
            RepositoryConfiguration(
                name="b", lionweb_version=LionWebVersion.V2023_1, history=True
            )
        )
        repo_client.create_repository(
            RepositoryConfiguration(
                name="c", lionweb_version=LionWebVersion.V2024_1, history=False
            )
        )
        repo_client.create_repository(
            RepositoryConfiguration(
                name="d", lionweb_version=LionWebVersion.V2024_1, history=True
            )
        )
        repos = repo_client.list_repositories()
        self.assertEqual(
            [
                RepositoryConfiguration(
                    name="default",
                    lionweb_version=LionWebVersion.V2023_1,
                    history=False,
                ),
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
                ),
            ],
            repos,
        )
        # All tests should go back to the initial situation
        repo_client.delete_repository("a")
        repo_client.delete_repository("b")
        repo_client.delete_repository("c")
        repo_client.delete_repository("d")
