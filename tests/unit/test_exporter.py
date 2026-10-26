import json
from app.models import Chunk
from app.services.exporter import ChunkExporter


def test_export_to_json_success():
    # Arrange
    chunks = [
        Chunk(chunk_index=0, text="Pierwszy fragment z polskimi znakami: ąęć", token_count=6),
        Chunk(chunk_index=1, text="Drugi fragment tekstu", token_count=3),
    ]

    # Act
    raw_json = ChunkExporter.to_json(chunks)
    parsed = json.loads(raw_json)

    # Assert
    assert len(parsed) == 2
    assert parsed[0]["chunk_index"] == 0
    assert parsed[0]["text"] == "Pierwszy fragment z polskimi znakami: ąęć"
    assert parsed[0]["token_count"] == 6
    assert parsed[1]["chunk_index"] == 1
    assert parsed[1]["token_count"] == 3


def test_export_to_json_empty_list():
    # Arrange
    chunks = []

    # Act
    raw_json = ChunkExporter.to_json(chunks)
    parsed = json.loads(raw_json)

    # Assert
    assert parsed == []


def test_export_to_csv_success():
    # Arrange
    chunks = [
        Chunk(chunk_index=0, text="Tekst testowy", token_count=2),
        Chunk(chunk_index=1, text="Kolejny wiersz", token_count=2),
    ]

    # Act
    csv_content = ChunkExporter.to_csv(chunks)
    lines = [line.strip() for line in csv_content.strip().split("\n")]

    # Assert
    assert lines[0] == "chunk_index,token_count,text"
    assert lines[1] == "0,2,Tekst testowy"
    assert lines[2] == "1,2,Kolejny wiersz"


def test_export_to_csv_empty_list():
    # Arrange
    chunks = []

    # Act
    csv_content = ChunkExporter.to_csv(chunks)
    lines = [line.strip() for line in csv_content.strip().split("\n")]

    # Assert
    assert len(lines) == 1
    assert lines[0] == "chunk_index,token_count,text"


def test_export_to_csv_handles_special_characters():
    # Arrange
    chunks = [
        Chunk(chunk_index=0, text='Tekst z przecinkiem, oraz "cudzysłowem"', token_count=5)
    ]

    # Act
    csv_content = ChunkExporter.to_csv(chunks)

    # Assert
    assert '0,5,"Tekst z przecinkiem, oraz ""cudzysłowem"""' in csv_content