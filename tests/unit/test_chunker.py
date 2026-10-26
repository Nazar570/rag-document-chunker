import pytest
from app.services.chunker import (
    WordChunkingStrategy,
    CharacterChunkingStrategy,
    ChunkingContext
)


def test_word_chunking_standard_split(word_strategy: WordChunkingStrategy):
    # Arrange
    text = "one two three four five six seven"
    chunk_size = 3
    overlap = 1
    expected = [
        "one two three",
        "three four five",
        "five six seven"
    ]

    # Act
    result = word_strategy.split(text, chunk_size, overlap)

    # Assert
    assert result == expected


def test_word_chunking_no_overlap(word_strategy: WordChunkingStrategy):
    # Arrange
    text = "alpha beta gamma delta"
    chunk_size = 2
    overlap = 0
    expected = ["alpha beta", "gamma delta"]

    # Act
    result = word_strategy.split(text, chunk_size, overlap)

    # Assert
    assert result == expected


def test_word_chunking_text_shorter_than_chunk_size(word_strategy: WordChunkingStrategy):
    # Arrange
    text = "short text"
    chunk_size = 5
    overlap = 1
    expected = ["short text"]

    # Act
    result = word_strategy.split(text, chunk_size, overlap)

    # Assert
    assert result == expected


def test_word_chunking_empty_and_whitespace_text(word_strategy: WordChunkingStrategy):
    # Arrange
    empty_text = ""
    whitespace_text = "    \n\t   "

    # Act
    res_empty = word_strategy.split(empty_text, chunk_size=5, overlap=1)
    res_whitespace = word_strategy.split(whitespace_text, chunk_size=5, overlap=1)

    # Assert
    assert res_empty == []
    assert res_whitespace == []


def test_word_chunking_raises_value_error_on_invalid_chunk_size(word_strategy: WordChunkingStrategy):
    # Arrange
    text = "sample text"
    invalid_chunk_size = 0
    overlap = 0

    # Act & Assert
    with pytest.raises(ValueError, match="chunk_size must be positive"):
        word_strategy.split(text, chunk_size=invalid_chunk_size, overlap=overlap)


def test_word_chunking_raises_value_error_on_negative_overlap(word_strategy: WordChunkingStrategy):
    # Arrange
    text = "sample text"
    chunk_size = 5
    invalid_overlap = -1

    # Act & Assert
    with pytest.raises(ValueError, match="overlap cannot be negative"):
        word_strategy.split(text, chunk_size=chunk_size, overlap=invalid_overlap)


def test_word_chunking_raises_value_error_when_overlap_ge_chunk_size(word_strategy: WordChunkingStrategy):
    # Arrange
    text = "sample text"
    chunk_size = 4
    invalid_overlap = 4

    # Act & Assert
    with pytest.raises(ValueError, match="overlap must be smaller than chunk_size"):
        word_strategy.split(text, chunk_size=chunk_size, overlap=invalid_overlap)


def test_char_chunking_standard_split(char_strategy: CharacterChunkingStrategy):
    # Arrange
    text = "abcdefghij"
    chunk_size = 4
    overlap = 1
    expected = [
        "abcd",
        "defg",
        "ghij"
    ]

    # Act
    result = char_strategy.split(text, chunk_size, overlap)

    # Assert
    assert result == expected


def test_char_chunking_no_overlap(char_strategy: CharacterChunkingStrategy):
    # Arrange
    text = "abcdef"
    chunk_size = 3
    overlap = 0
    expected = ["abc", "def"]

    # Act
    result = char_strategy.split(text, chunk_size, overlap)

    # Assert
    assert result == expected


def test_char_chunking_empty_text(char_strategy: CharacterChunkingStrategy):
    # Arrange
    text = ""

    # Act
    result = char_strategy.split(text, chunk_size=5, overlap=1)

    # Assert
    assert result == []


def test_chunking_context_delegates_execution(chunking_context: ChunkingContext):
    # Arrange
    text = "one two three four"
    chunk_size = 2
    overlap = 0
    expected = ["one two", "three four"]

    # Act
    result = chunking_context.execute(text, chunk_size, overlap)

    # Assert
    assert result == expected


def test_chunking_context_allows_runtime_strategy_swap(
    chunking_context: ChunkingContext,
    char_strategy: CharacterChunkingStrategy
):
    # Arrange
    text = "abcdef"
    chunk_size = 3
    overlap = 0
    expected_chars = ["abc", "def"]

    # Act
    chunking_context.set_strategy(char_strategy)
    result = chunking_context.execute(text, chunk_size, overlap)

    # Assert
    assert result == expected_chars