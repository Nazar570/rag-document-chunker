from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class ProcessDocumentRequest(BaseModel):
    text: str = Field(..., min_length=1)
    chunk_size: int = Field(default=5, gt=0)
    overlap: int = Field(default=1, ge=0)
    strategy: Literal["word", "character"] = "word"


class ChunkResponse(BaseModel):
    id: int
    chunk_index: int
    text: str
    token_count: int

    model_config = ConfigDict(from_attributes=True)


class DocumentResponse(BaseModel):
    id: int
    original_text: str
    created_at: datetime
    chunks: list[ChunkResponse]

    model_config = ConfigDict(from_attributes=True)