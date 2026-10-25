from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
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
from app.services.exporter import ChunkExporter

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RAG Document Chunker API")
cleaner = TextCleaner()

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", include_in_schema=False)
def serve_ui():
    return FileResponse("app/static/index.html")


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


@app.get("/api/documents/{document_id}/export")
def export_document_chunks(document_id: int, format: str = "json", db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="document not found"
        )

    if format == "csv":
        content = ChunkExporter.to_csv(document.chunks)
        media_type = "text/csv"
        filename = f"chunks_doc_{document_id}.csv"
    elif format == "json":
        content = ChunkExporter.to_json(document.chunks)
        media_type = "application/json"
        filename = f"chunks_doc_{document_id}.json"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported format. Use 'json' or 'csv'."
        )

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )