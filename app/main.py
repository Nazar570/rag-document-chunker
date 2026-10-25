from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.models import Document, Chunk
from app.schemas import ProcessDocumentRequest, DocumentResponse
from app.services.cleaner import TextCleaner
from app.services.chunker import (
    ChunkingContext,
    WordChunkingStrategy,
    CharacterChunkingStrategy
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RAG Document Chunker API")
cleaner = TextCleaner()


@app.post("/api/documents/process", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def process_document(payload: ProcessDocumentRequest, db: Session = Depends(get_db)):
    if payload.overlap >= payload.chunk_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="overlap must be smaller than chunk_size"
        )

    cleaned_text = cleaner.clean(payload.text)
    if not cleaned_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="text cannot be empty after cleaning"
        )

    if payload.strategy == "character":
        strategy = CharacterChunkingStrategy()
    else:
        strategy = WordChunkingStrategy()

    context = ChunkingContext(strategy)
    raw_chunks = context.execute(cleaned_text, payload.chunk_size, payload.overlap)

    document = Document(original_text=payload.text)
    db.add(document)
    db.flush()

    for idx, chunk_content in enumerate(raw_chunks):
        token_count = len(chunk_content.split()) if payload.strategy == "word" else len(chunk_content)
        chunk = Chunk(
            document_id=document.id,
            chunk_index=idx,
            text=chunk_content,
            token_count=token_count
        )
        db.add(chunk)

    db.commit()
    db.refresh(document)
    return document


@app.get("/api/documents", response_model=list[DocumentResponse])
def get_documents(db: Session = Depends(get_db)):
    return db.query(Document).all()


@app.get("/api/documents/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="document not found"
        )
    return document