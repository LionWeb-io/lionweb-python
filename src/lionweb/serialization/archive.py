from collections.abc import Callable
from os import PathLike
from typing import List

from lionweb import LionWebVersion
from lionweb.serialization import SerializationChunk
from lionweb.serialization.protobuf_serialization import ProtoBufSerialization


def process_archive(
    filename: str | PathLike,
    chunk_processor: Callable[[int, int, SerializationChunk], None],
) -> None:
    ps = ProtoBufSerialization(LionWebVersion.V2023_1)
    import zipfile

    with zipfile.ZipFile(filename, "r") as zf:
        n_elements = len(zf.namelist())
        i = 0
        for name in zf.namelist():
            with zf.open(name) as entry_file:
                content = entry_file.read()
            content = zf.read(name)  # bytes
            chunk = ps.read_chunk_from_bytes(content)
            del content
            chunk_processor(i, n_elements, chunk)
            i += 1


def load_archive(filename) -> List[SerializationChunk]:
    chunks = []
    process_archive(filename, lambda i, n, chunk: chunks.append(chunk))
    return chunks
