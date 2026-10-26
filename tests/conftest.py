import pytest
from app.services.cleaner import TextCleaner
from app.services.chunker import (
    WordChunkingStrategy,
    CharacterChunkingStrategy,
    ChunkingContext
)


@pytest.fixture
def text_cleaner():
    return TextCleaner()


@pytest.fixture
def word_strategy():
    return WordChunkingStrategy()


@pytest.fixture
def char_strategy():
    return CharacterChunkingStrategy()


@pytest.fixture
def chunking_context(word_strategy):
    return ChunkingContext(strategy=word_strategy)