import zipfile

from lionweb.client import BulkImport, Client
from lionweb.serialization import LowLevelJsonSerialization


def load_repository_archive(
    client: Client, archive_path: str, upload_threshold=250_000
):
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


