from sqlalchemy.orm import Session
from app.models import Document, Chunk


def test_document_chunk_relationship_creation(db_session: Session):
    # Arrange
    doc = Document(original_text="Raw document content")
    db_session.add(doc)
    db_session.commit()

    chunk1 = Chunk(document_id=doc.id, chunk_index=0, text="Raw document", token_count=2)
    chunk2 = Chunk(document_id=doc.id, chunk_index=1, text="content", token_count=1)
    db_session.add_all([chunk1, chunk2])
    db_session.commit()

    # Act
    saved_doc = db_session.query(Document).filter(Document.id == doc.id).first()

    # Assert
    assert saved_doc is not None
    assert len(saved_doc.chunks) == 2
    assert saved_doc.chunks[0].text == "Raw document"


def test_document_cascade_delete_removes_chunks(db_session: Session):
    # Arrange
    doc = Document(original_text="To be deleted")
    db_session.add(doc)
    db_session.commit()

    chunk = Chunk(document_id=doc.id, chunk_index=0, text="Temporary chunk", token_count=2)
    db_session.add(chunk)
    db_session.commit()

    # Act
    db_session.delete(doc)
    db_session.commit()

    remaining_chunks = db_session.query(Chunk).filter(Chunk.document_id == doc.id).all()

    # Assert
    assert remaining_chunks == []