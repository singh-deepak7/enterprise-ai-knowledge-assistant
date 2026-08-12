from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ChunkMetadata:
    chunk_id: str
    chunk_index: int
    total_chunks: int
    chunk_size: int
    metadata: dict[str, Any]