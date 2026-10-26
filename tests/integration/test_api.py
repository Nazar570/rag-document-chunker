from fastapi.testclient import TestClient


def test_process_document_success_word_strategy(client: TestClient):
    # Arrange
    payload = {
        "text": "<p>Alpha beta gamma delta epsilon.</p>",
        "chunk_size": 3,
        "overlap": 1,
        "strategy": "word"
    }

    # Act
    response = client.post("/api/documents/process", json=payload)
    data = response.json()

    # Assert
    assert response.status_code == 201
    assert data["id"] is not None
    assert data["original_text"] == payload["text"]
    assert len(data["chunks"]) == 2
    assert data["chunks"][0]["chunk_index"] == 0
    assert data["chunks"][0]["text"] == "Alpha beta gamma"
    assert data["chunks"][0]["token_count"] == 3
    assert data["chunks"][1]["chunk_index"] == 1
    assert data["chunks"][1]["text"] == "gamma delta epsilon."
    assert data["chunks"][1]["token_count"] == 3


def test_process_document_success_character_strategy(client: TestClient):
    # Arrange
    payload = {
        "text": "ABCDEFGH",
        "chunk_size": 4,
        "overlap": 1,
        "strategy": "character"
    }

    # Act
    response = client.post("/api/documents/process", json=payload)
    data = response.json()

    # Assert
    assert response.status_code == 201
    assert len(data["chunks"]) == 3
    assert data["chunks"][0]["text"] == "ABCD"
    assert data["chunks"][1]["text"] == "DEFG"
    assert data["chunks"][2]["text"] == "GH"


def test_process_document_validation_overlap_greater_than_chunk_size(client: TestClient):
    # Arrange
    payload = {
        "text": "Some valid document text",
        "chunk_size": 3,
        "overlap": 4,
        "strategy": "word"
    }

    # Act
    response = client.post("/api/documents/process", json=payload)
    data = response.json()

    # Assert
    assert response.status_code == 400
    assert data["detail"] == "overlap must be smaller than chunk_size"


def test_process_document_validation_empty_after_cleaning(client: TestClient):
    # Arrange
    payload = {
        "text": "<div>   \n\t  </div>",
        "chunk_size": 5,
        "overlap": 1,
        "strategy": "word"
    }

    # Act
    response = client.post("/api/documents/process", json=payload)
    data = response.json()

    # Assert
    assert response.status_code == 400
    assert data["detail"] == "text cannot be empty after cleaning"


def test_process_document_pydantic_schema_validation_error(client: TestClient):
    # Arrange
    payload = {
        "text": "Text without positive chunk size",
        "chunk_size": 0,
        "overlap": 0,
        "strategy": "word"
    }

    # Act
    response = client.post("/api/documents/process", json=payload)

    # Assert
    assert response.status_code == 422


def test_get_documents_list_flow(client: TestClient):
    # Arrange
    client.post(
        "/api/documents/process",
        json={"text": "First doc content", "chunk_size": 2, "overlap": 0, "strategy": "word"}
    )
    client.post(
        "/api/documents/process",
        json={"text": "Second doc content", "chunk_size": 2, "overlap": 0, "strategy": "word"}
    )

    # Act
    response = client.get("/api/documents")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["id"] == 1
    assert data[1]["id"] == 2


def test_get_document_by_id_success(client: TestClient):
    # Arrange
    create_res = client.post(
        "/api/documents/process",
        json={"text": "Target document to fetch", "chunk_size": 2, "overlap": 0, "strategy": "word"}
    )
    doc_id = create_res.json()["id"]

    # Act
    response = client.get(f"/api/documents/{doc_id}")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["id"] == doc_id
    assert data["original_text"] == "Target document to fetch"
    assert len(data["chunks"]) == 2


def test_get_document_by_id_not_found(client: TestClient):
    # Arrange
    non_existing_id = 9999

    # Act
    response = client.get(f"/api/documents/{non_existing_id}")
    data = response.json()

    # Assert
    assert response.status_code == 404
    assert data["detail"] == "document not found"


def test_export_document_chunks_json(client: TestClient):
    # Arrange
    create_res = client.post(
        "/api/documents/process",
        json={"text": "Exportable test content", "chunk_size": 2, "overlap": 0, "strategy": "word"}
    )
    doc_id = create_res.json()["id"]

    # Act
    response = client.get(f"/api/documents/{doc_id}/export?format=json")

    # Assert
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    assert f'filename=chunks_doc_{doc_id}.json' in response.headers["content-disposition"]
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["chunk_index"] == 0
    assert data[0]["text"] == "Exportable test"


def test_export_document_chunks_csv(client: TestClient):
    # Arrange
    create_res = client.post(
        "/api/documents/process",
        json={"text": "First second third", "chunk_size": 2, "overlap": 0, "strategy": "word"}
    )
    doc_id = create_res.json()["id"]

    # Act
    response = client.get(f"/api/documents/{doc_id}/export?format=csv")

    # Assert
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert f'filename=chunks_doc_{doc_id}.csv' in response.headers["content-disposition"]
    lines = response.text.strip().split("\r\n" if "\r\n" in response.text else "\n")
    assert lines[0] == "chunk_index,token_count,text"
    assert "0,2,First second" in lines[1]


def test_export_document_chunks_invalid_format(client: TestClient):
    # Arrange
    create_res = client.post(
        "/api/documents/process",
        json={"text": "Some text", "chunk_size": 2, "overlap": 0, "strategy": "word"}
    )
    doc_id = create_res.json()["id"]

    # Act
    response = client.get(f"/api/documents/{doc_id}/export?format=unsupported_format")
    data = response.json()

    # Assert
    assert response.status_code == 400
    assert "Unsupported format" in data["detail"]


def test_serve_ui_homepage(client: TestClient):
    # Arrange / Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "RAG Document Chunker" in response.text