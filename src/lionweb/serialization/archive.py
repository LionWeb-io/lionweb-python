import time
from typing import List

from lionweb import LionWebVersion
from lionweb.serialization import SerializationChunk
from lionweb.serialization.protobuf_serialization import ProtoBufSerialization


def load_archive(filename) -> List[SerializationChunk]:
    ps = ProtoBufSerialization(LionWebVersion.V2023_1)
    start = time.time()
    chunks: List[SerializationChunk] = []
    import zipfile

    with zipfile.ZipFile(filename, "r") as zf:
        for name in zf.namelist():
            with zf.open(name) as entry_file:
                content = entry_file.read()
            content = zf.read(name)  # bytes
            chunk = ps.read_chunk_from_bytes(content)
            del content
            chunks.append(chunk)
    end = time.time()

    print("Elapsed:", end - start, "seconds")
    print(f"Chunks {len(chunks)}")
    return chunks
