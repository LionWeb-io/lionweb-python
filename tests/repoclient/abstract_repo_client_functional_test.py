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
MODEL_REPO_PORT = 3005
DB_CONTAINER_PORT = 5432

class AbstractRepoClientFunctionalTest:
    """Base class for integration tests with PostgreSQL and Model Repository."""

    @pytest.fixture(scope="session", autouse=True)
    def setup(self):
        """Sets up the PostgreSQL container and the Model Repository service."""

        network = Network()

        # Start PostgreSQL
        self.db = PostgresContainer(DB_IMAGE, username=DB_USER, password=DB_PASSWORD, dbname=DB_NAME)
        self.db.with_network(network)
        self.db.with_network_aliases("mypgdb")
        self.db.with_exposed_ports(DB_CONTAINER_PORT)
        self.db.start()

        # Get database connection details
        db_host = self.db.get_container_host_ip()
        db_port = self.db.get_exposed_port()

        # Start Model Repository
        self.model_repo = DockerContainer(REPO_IMAGE)
        self.model_repo.with_env("PGHOST", db_host)
        self.model_repo.with_env("PGPORT", str(db_port))
        self.model_repo.with_env("PGUSER", DB_USER)
        self.model_repo.with_env("PGPASSWORD", DB_PASSWORD)
        self.model_repo.with_env("PGDB", DB_NAME)
        self.model_repo.with_env("LIONWEB_VERSION", "1.0")  # Replace with actual version
        self.model_repo.with_exposed_ports(MODEL_REPO_PORT)

        # Wait until the model repository is ready
        wait_for_logs(self.model_repo, "Server started", timeout=30)
        self.model_repo.start()

        # Get mapped port
        self.model_repo_port = self.model_repo.get_exposed_port(MODEL_REPO_PORT)

        # Expose port for tests
        os.environ["MODEL_REPO_PORT"] = str(self.model_repo_port)

        # Wait for the server to be ready
        self.wait_for_model_repo()

        yield  # Run tests

        # Cleanup
        self.model_repo.stop()
        self.db.stop()

    def wait_for_model_repo(self):
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

class MyTest(AbstractRepoClientFunctionalTest, unittest.TestCase):

    def test_get_data(self):
        """Test retrieving data from the model repository."""
        response = requests.get(f"{MODEL_REPO_URL}/api/data")
        assert response.status_code == 200
        assert "result" in response.json()


    def test_post_data(self):
        """Test sending data to the model repository."""
        payload = {"name": "TestItem"}
        response = requests.post(f"{MODEL_REPO_URL}/api/data", json=payload)
        assert response.status_code == 201
        assert response.json()["name"] == "TestItem"