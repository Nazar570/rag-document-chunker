from abc import ABC, abstractmethod


class ChunkingStrategy(ABC):
    @staticmethod
    def _validate_params(chunk_size: int, overlap: int) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0:
            raise ValueError("overlap cannot be negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

    @abstractmethod
    def split(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        pass


class WordChunkingStrategy(ChunkingStrategy):
    def split(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        if not text:
            return []
        self._validate_params(chunk_size, overlap)

        words = text.split()
        if not words:
            return []

        step = chunk_size - overlap
        chunks = []

        for i in range(0, len(words), step):
            chunks.append(" ".join(words[i:i + chunk_size]))
            if i + chunk_size >= len(words):
                break

        return chunks


class CharacterChunkingStrategy(ChunkingStrategy):
    def split(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        if not text:
            return []
        self._validate_params(chunk_size, overlap)

        step = chunk_size - overlap
        chunks = []

        for i in range(0, len(text), step):
            chunks.append(text[i:i + chunk_size])
            if i + chunk_size >= len(text):
                break

        return chunks


class ChunkingContext:
    def __init__(self, strategy: ChunkingStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: ChunkingStrategy) -> None:
        self.strategy = strategy

    def split(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        return self.strategy.split(text, chunk_size, overlap)


CHUNKING_STRATEGIES: dict[str, type[ChunkingStrategy]] = {
    "word": WordChunkingStrategy,
    "character": CharacterChunkingStrategy,
}


def get_chunking_strategy(name: str) -> ChunkingStrategy:
    strategy_cls = CHUNKING_STRATEGIES.get(name, WordChunkingStrategy)
    return strategy_cls()