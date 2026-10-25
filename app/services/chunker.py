from abc import ABC, abstractmethod


class ChunkingStrategy(ABC):
    @abstractmethod
    def split(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        pass


class WordChunkingStrategy(ChunkingStrategy):
    def split(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        if not text:
            return []
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0:
            raise ValueError("overlap cannot be negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        words = text.split()
        if not words:
            return []

        step = chunk_size - overlap
        chunks = []

        for i in range(0, len(words), step):
            chunk_slice = words[i:i + chunk_size]
            chunks.append(" ".join(chunk_slice))
            if i + chunk_size >= len(words):
                break

        return chunks


class CharacterChunkingStrategy(ChunkingStrategy):
    def split(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        if not text:
            return []
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0:
            raise ValueError("overlap cannot be negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        step = chunk_size - overlap
        chunks = []

        for i in range(0, len(text), step):
            chunks.append(text[i:i + chunk_size])
            if i + chunk_size >= len(text):
                break

        return chunks


class ChunkingContext:
    def __init__(self, strategy: ChunkingStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: ChunkingStrategy) -> None:
        self._strategy = strategy

    def execute(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        return self._strategy.split(text, chunk_size, overlap)