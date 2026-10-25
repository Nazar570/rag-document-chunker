import csv
import io
import json
from typing import Sequence
from app.models import Chunk


class ChunkExporter:
    @staticmethod
    def to_json(chunks: Sequence[Chunk]) -> str:
        data = [
            {
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "token_count": chunk.token_count
            }
            for chunk in chunks
        ]
        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def to_csv(chunks: Sequence[Chunk]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["chunk_index", "token_count", "text"])
        for chunk in chunks:
            writer.writerow([chunk.chunk_index, chunk.token_count, chunk.text])
        return output.getvalue()