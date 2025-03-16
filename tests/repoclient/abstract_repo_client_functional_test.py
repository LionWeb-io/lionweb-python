import os
import time
import unittest

import pytest
import requests
from testcontainers.core.network import Network
from testcontainers.postgres import PostgresContainer
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

# Constants
DB_IMAGE = "postgres:16.1"
REPO_IMAGE = "your-node-repo-image:latest"  # Replace with your Node.js image
DB_USER = "postgres"
DB_PASSWORD = "lionweb"
DB_NAME = "lionweb_test"
MODEL_REPO_PORT = 7101
DB_CONTAINER_PORT = 7100

class AbstractRepoClientFunctionalTest:
    """Base class for integration tests with PostgreSQL and Model Repository."""

    @pytest.fixture(scope="session", autouse=True)
    def setup(cls):
        """Sets up the PostgreSQL container and the Model Repository service."""

        network = Network()

        # Start PostgreSQL
        cls.db = PostgresContainer(DB_IMAGE, username=DB_USER, password=DB_PASSWORD, dbname=DB_NAME)
        cls.db.with_network(network)
        cls.db.with_network_aliases("mypgdb")
        cls.db.with_exposed_ports(DB_CONTAINER_PORT)  # Expose the correct port
        cls.db.with_bind_ports(5432, DB_CONTAINER_PORT)
        cls.db.start()

        # Get database connection details
        db_host = cls.db.get_container_host_ip()
        db_port = cls.db.get_exposed_port()

        # Start Model Repository
        cls.model_repo = DockerContainer(REPO_IMAGE)
        cls.model_repo.with_env("PGHOST", db_host)
        cls.model_repo.with_env("PGPORT", str(db_port))
        cls.model_repo.with_env("PGUSER", DB_USER)
        cls.model_repo.with_env("PGPASSWORD", DB_PASSWORD)
        cls.model_repo.with_env("PGDB", DB_NAME)
        cls.model_repo.with_env("LIONWEB_VERSION", "1.0")  # Replace with actual version
        cls.model_repo.with_exposed_ports(MODEL_REPO_PORT)

        # Wait until the model repository is ready
        wait_for_logs(cls.model_repo, "Server started", timeout=30)
        cls.model_repo.start()

        # Get mapped port
        cls.model_repo_port = cls.model_repo.get_exposed_port(MODEL_REPO_PORT)

        # Expose port for tests
        os.environ["MODEL_REPO_PORT"] = str(cls.model_repo_port)

        # Wait for the server to be ready
        cls.wait_for_model_repo()

    @classmethod
    def teardown_class(cls):
        """Cleanup the containers after tests."""
        cls.model_repo.stop()
        cls.db.stop()

    @classmethod
    def wait_for_model_repo(cls):
        """Waits for the model repository API to be available."""
        url = f"http://localhost:{self.model_repo_port}/health"
        for _ in range(10):  # Try for ~50 seconds
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print("Model repository is ready!")
                    return
            except requests.ConnectionError:
                pass
            time.sleep(5)
        raise RuntimeError("Model repository did not start in time!")

    def assert_lw_trees_are_equal(self, a, b):
        """Dummy comparison function (replace with real comparison logic)."""
        assert a == b, f"Differences between {a} and {b}"

import requests

MODEL_REPO_URL = f"http://localhost:{os.getenv('MODEL_REPO_PORT')}"

