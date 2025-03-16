import os
import time
import unittest
from threading import Thread

import requests
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.postgres import PostgresContainer

# Constants
DB_IMAGE = "postgres:16.1"
REPO_IMAGE = "model_repo_for_lwpython_tests"  # Replace with your Node.js image
DB_USER = "postgres"
DB_PASSWORD = "lionweb"
DB_NAME = "lionweb_test"
DB_HOST = "pgdb_for_lwpython_tests"
MODEL_REPO_PORT = 3005
DB_CONTAINER_PORT = 7100


class AbstractRepoClientFunctionalTest(unittest.TestCase):
    """Base class for integration tests with PostgreSQL and Model Repository."""

    @classmethod
    def setUpClass(cls):
        """Sets up the PostgreSQL container and the Model Repository service."""

        cls.network = Network()
        cls.network.create()

        # Start PostgreSQL
        cls.db = PostgresContainer(
            DB_IMAGE, username=DB_USER, password=DB_PASSWORD, dbname=DB_NAME
        )
        cls.db.with_network(cls.network)
        cls.db.with_network_aliases(DB_HOST)
        cls.db.with_exposed_ports(DB_CONTAINER_PORT)  # Expose the correct port
        cls.db.with_bind_ports(5432, DB_CONTAINER_PORT)
        cls.db.start()

        # Get database connection details
        db_host = cls.db.get_container_host_ip()
        db_port = cls.db.get_exposed_port(5432)

        # Print PostgreSQL logs in a separate thread
        cls._start_log_thread(cls.db, "POSTGRESQL")

        # Start Model Repository
        cls.model_repo = DockerContainer(REPO_IMAGE)
        cls.model_repo.with_network(cls.network)
        cls.model_repo.with_env("PGHOST", db_host)
        cls.model_repo.with_env("PGPORT", str(db_port))
        cls.model_repo.with_env("PGUSER", DB_USER)
        cls.model_repo.with_env("PGPASSWORD", DB_PASSWORD)
        cls.model_repo.with_env("PGDB", DB_NAME)
        cls.model_repo.with_env("LIONWEB_VERSION", "1.0")  # Replace with actual version
        cls.model_repo.with_exposed_ports(MODEL_REPO_PORT)

        # Start the Model Repository and capture logs
        cls.model_repo.start()
        cls._start_log_thread(cls.model_repo, "MODEL_REPO")

        # Get mapped port
        cls.model_repo_port = cls.model_repo.get_exposed_port(MODEL_REPO_PORT)

        # Wait until the model repository is ready
        # Wait for the server to be ready
        print("Waiting for model repo...")
        cls._wait_for_model_repo()
        print("Model repo is up: let's start testing")


        # Expose port for tests
        os.environ["MODEL_REPO_PORT"] = str(cls.model_repo_port)
        # Debugging Output
        print(f"[DEBUG] Model Repository should be reachable at: http://localhost:{cls.model_repo_port}")
        print(f"[DEBUG] Environment MODEL_REPO_PORT = {os.getenv('MODEL_REPO_PORT')}")
        time.sleep(2)

    @classmethod
    def _start_log_thread(cls, container, container_name):
        """Starts a background thread to continuously print container logs."""

        def log_printer():
            for line in container.get_wrapped_container().logs(stream=True):
                print(f"[{container_name}] {line.decode().strip()}")

        thread = Thread(target=log_printer, daemon=True)
        thread.start()

    @classmethod
    def tearDownClass(cls):
        """Cleanup the containers after tests."""
        cls.model_repo.stop()
        cls.db.stop()

    @classmethod
    def _wait_for_model_repo(cls):
        """Waits for the model repository to be available."""
        # cls._wait_for_logs(cls.model_repo, "Server is running", timeout=30)

        """Waits for the Model Repository API to be available by checking the root endpoint."""
        url = f"http://localhost:{cls.model_repo_port}/"
        max_attempts = 30  # Retry up to 60 seconds

        for attempt in range(max_attempts):
            try:
                print(f"[DEBUG] Checking Model Repo readiness (attempt {attempt + 1}/{max_attempts}) at {url}...")
                response = requests.get(url, timeout=5)

                if response.status_code in [200, 404]:  # Accepts 404 as it confirms a response
                    print(f"[DEBUG] Model Repo is READY! Status: {response.status_code}")
                    return

            except requests.ConnectionError:
                print("[DEBUG] Model Repo API not ready yet... retrying in 2s")

            time.sleep(2)  # Wait before retrying

        # Print logs before failing
        print("[ERROR] Model Repo did not become ready in time! Last logs:")
        print(cls.model_repo.get_wrapped_container().logs(tail=50).decode())
        raise RuntimeError("[ERROR] Model Repo API did not become ready in time!")

    @classmethod
    def _wait_for_logs(cls, container, expected_log, timeout=30):
        """Waits until the expected log appears in the container logs."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            logs = container.get_wrapped_container().logs().decode()
            if expected_log in logs:
                print(f"[MODEL_REPO] Detected '{expected_log}', Model Repo is ready!")
                return
            time.sleep(1)
        raise RuntimeError(f"[MODEL_REPO] '{expected_log}' not found in logs after {timeout} seconds!")

    def assert_lw_trees_are_equal(self, a, b):
        """Dummy comparison function (replace with real comparison logic)."""
        assert a == b, f"Differences between {a} and {b}"


import requests

MODEL_REPO_URL = f"http://localhost:{os.getenv('MODEL_REPO_PORT')}"
