import zipfile

from lionweb.client import BulkImport, Client
from lionweb.serialization import LowLevelJsonSerialization


def load_repository_archive(
    client: Client, archive_path: str, upload_threshold: int = 250_000
) -> None:
    """Load a repository archive (a zip of JSON serialization chunks) into a server.

    The archive is read entry by entry; nodes are accumulated into a BulkImport
    and uploaded in batches once the number of pending nodes exceeds
    `upload_threshold`, to limit memory usage and request size.

    Args:
        client: The client used to talk to the LionWeb repository server.
        archive_path: Path to the zip archive containing `.json` serialization chunks.
        upload_threshold: Maximum number of pending nodes to accumulate before
            triggering an upload.
    """
    import time

    def upload(bulk_import: BulkImport) -> int:
        if bulk_import.number_of_nodes() == 0:
            return 0
        print(f"Uploading {bulk_import.number_of_nodes()} nodes")
        n_nodes = bulk_import.number_of_nodes()
        client.bulk_import_using_json(bulk_import)
        bulk_import.clear()
        return n_nodes

    bulk_import = BulkImport()
    total_nodes = 0

    start = time.perf_counter()
    with zipfile.ZipFile(archive_path, "r") as zip_file:
        file_list = zip_file.namelist()
        ordinal = 1
        for filename in file_list:
            if filename.endswith(".json"):
                content = zip_file.read(filename).decode("utf-8")
                chunk = LowLevelJsonSerialization().deserialize_serialization_block_from_string(
                    content
                )
                print(
                    f"  [{ordinal}/{len(file_list)}] Adding {len(chunk.classifier_instances)} nodes from {filename}"
                )
                bulk_import.add_nodes(chunk.classifier_instances)
                if bulk_import.number_of_nodes() > upload_threshold:
                    total_nodes += upload(bulk_import)
            ordinal += 1
    total_nodes += upload(bulk_import)
    end = time.perf_counter()
    elapsed_seconds = end - start
    print(f"Uploaded {total_nodes} nodes in {elapsed_seconds:.3f} seconds")
