# Testowanie i Jakość Oprogramowania II

## Autor

- **Autor:** Nazar Suslyk
- **Kierunek:** Informatyka
- **Specjalność:** Inżynieria Systemów Inteligentnych (ISI)
- **Wydział:** Wydział Politechniczny, Akademia Tarnowska
- **Prowadzący:** dr inż. Tomasz Gądek

---

## Temat projektu

**RAG Document Chunker & Preprocessor** — moduł przetwarzania wstępnego, czyszczenia oraz parametrycznej segmentacji tekstu na potrzeby systemów Retrieval-Augmented Generation (RAG) z interfejsem webowym i silnikiem eksportu.

---

## Opis projektu

Aplikacja rozwiązuje kluczowy problem w architekturze systemów RAG (Retrieval-Augmented Generation) oraz LLM: przygotowanie surowego, zanieczyszczonego tekstu (zawierającego znaczniki HTML, formatowanie Markdown i nadmiarowe białe znaki) do postaci zoptymalizowanych fragmentów (*chunków*) o kontrolowanym rozmiarze i zakładce (*overlap*).

### Główne funkcjonalności

1. **Pipeline czyszczenia tekstu (`TextCleaner`):**
   - Usuwanie znaczników HTML przy użyciu wyrażeń regularnych.
   - Ekstrakcja czystego tekstu z linków i elementów Markdown (nagłówki, pogrubienia, kursywy).
   - Normalizacja białych znaków (redukcja wielokrotnych spacji, tabulacji i znaków nowej linii).

2. **Parametryczna segmentacja tekstu (wzorzec projektowy *Strategy*):**
   - **WordChunkingStrategy:** Podział na poziomie całych słów z zachowaniem spójności leksykalnej.
   - **CharacterChunkingStrategy:** Podział na poziomie surowych znaków dla precyzyjnych ograniczeń okna kontekstowego.
   - Obsługa parametru zakładki (*overlap*) gwarantującego zachowanie ciągłości semantycznej pomiędzy sąsiednimi chunkami.

3. **Persystencja danych (SQLAlchemy ORM + SQLite):**
   - Relacja jeden-do-wielu (`Document` → `Chunk`).
   - Kaskadowe usuwanie danych powiązanych (`cascade="all, delete-orphan"`).

4. **Eksport danych (`ChunkExporter`):**
   - Eksport wygenerowanych chunków do formatu **JSON** (gotowego do wektoryzacji/embeddingów).
   - Eksport do formatu **CSV** (do analizy tabelarycznej i audytu).

5. **Graficzny interfejs użytkownika (UI):**
   - Responsywny dashboard oparty na HTML5, JavaScript (Fetch API) i Bootstrap 5.

### Zastosowane zasady inżynierii oprogramowania

- **SOLID:**
  - *Single Responsibility Principle (SRP):* Separacja odpowiedzialności za czyszczenie (`TextCleaner`), podział (`ChunkingStrategy`), eksport (`ChunkExporter`) i obsługę zapytań HTTP (`main.py`).
  - *Open/Closed Principle (OCP):* Dodanie nowej strategii podziału wymaga jedynie implementacji interfejsu `ChunkingStrategy`, bez modyfikacji istniejących klas.
  - *Dependency Inversion Principle (DIP):* Wstrzykiwanie sesji bazy danych poprzez mechanizm zależności FastAPI (`Depends(get_db)`).
- **Wzorce projektowe:** Wzorzec **Strategia (Strategy Pattern)** w module podziału tekstu.
- **Czysty kod:** Nazewnictwo klas, metod i zmiennych w języku angielskim, brak nieużywanych importów, pełne typowanie (*type hints*).

---

## Uruchomienie projektu

### Wymagania wstępne

- Python w wersji 3.10 lub nowszej.
- Menedżer pakietów `pip`.

### Instrukcja krok po kroku

1. **Sklonuj repozytorium:**

   ```bash
   git clone <URL_REPOZYTORIUM>
   cd rag-document-chunker
   ```

2. **Utwórz i aktywuj wirtualne środowisko (`venv`):**

   **Linux / macOS:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   **Windows (PowerShell):**

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Zainstaluj zależności:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Uruchom serwer deweloperski Uvicorn:**

   ```bash
   uvicorn app.main:app --reload
   ```

5. **Dostęp do aplikacji:**

   - **Interfejs webowy (UI):** http://127.0.0.1:8000/
   - **Interaktywna dokumentacja Swagger UI:** http://127.0.0.1:8000/docs

---

## Testy

Projekt posiada kompleksowy zestaw ponad 40 zautomatyzowanych testów zorganizowanych według standardu **AAA (Arrange-Act-Assert)**:

- **Arrange (Przygotuj):** Inicjalizacja danych wejściowych, obiektów i stanu początkowego.
- **Act (Działaj):** Wywołanie testowanej metody lub wysłanie symulowanego żądania HTTP.
- **Assert (Sprawdź):** Weryfikacja zgodności wyniku z wartością oczekiwaną.

W testach integracyjnych zastosowano pełną izolację bazy danych poprzez podmienienie bazy fizycznej na ulotną bazę w pamięci RAM (`sqlite:///:memory:` z pulą `StaticPool`) za pomocą mechanizmu `app.dependency_overrides`.

### Struktura katalogu testów

- `tests/conftest.py` — Centralna konfiguracja fixtur `pytest`, fabryka sesji testowej bazy w pamięci operacyjnej oraz instancja `TestClient(app)`.

**Testy jednostkowe (`tests/unit/`):**

- `tests/unit/test_cleaner.py` — Testy modułu `TextCleaner`: usuwanie HTML, Markdown, normalizacja spacji, obsługa pustych ciągów oraz testy parametryzowane (`@pytest.mark.parametrize`).
- `tests/unit/test_chunker.py` — Testy algorytmów podziału `WordChunkingStrategy`, `CharacterChunkingStrategy`, obsługa wartości brzegowych, walidacja błędów (`pytest.raises`) oraz dynamiczna zmiana strategii w `ChunkingContext`.
- `tests/unit/test_exporter.py` — Testy klasy `ChunkExporter`: generowanie formatu JSON (z obsługą znaków diakrytycznych) oraz formatu CSV (z poprawnym escapowaniem przecinków i cudzysłowów według RFC 4180).
- `tests/unit/test_models.py` — Testy jednostkowe modeli SQLAlchemy: weryfikacja relacji 1:N oraz kaskadowego usuwania chunków po skasowaniu dokumentu nadrzędnego.

**Testy integracyjne (`tests/integration/`):**

- `tests/integration/test_api.py` — Pełne testy przepływu API przy użyciu `TestClient`: tworzenie dokumentów, weryfikacja walidacji Pydantic (błędy 400 i 422), pobieranie listy dokumentów (200), pobieranie pojedynczego zasobu (200 i 404), endpointy eksportu plików (JSON/CSV) z nagłówkami `Content-Disposition` oraz serwowanie widoku UI.

### Uruchomienie testów

- **Uruchomienie wszystkich testów w trybie szczegółowym:**

  ```bash
  pytest
  ```

- **Uruchomienie wyłącznie testów jednostkowych:**

  ```bash
  pytest tests/unit/
  ```

- **Uruchomienie wyłącznie testów integracyjnych:**

  ```bash
  pytest tests/integration/
  ```

---

## Dokumentacja API

## Dokumentacja API

Aplikacja udostępnia interaktywną specyfikację w standardzie **OpenAPI 3.0** generowaną automatycznie przez framework FastAPI pod adresem:

* **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Tabela punktów końcowych (Endpoints)

| Metoda HTTP | Ścieżka URL | Opis operacji | Zwracane kody HTTP |
|---|---|---|---|
| `GET` | `/` | Serwowanie interfejsu graficznego użytkownika (HTML) | `200` |
| `POST` | `/api/documents/process` | Czyszczenie tekstu, podział na chunki i zapis do bazy | `201`, `400`, `422` |
| `GET` | `/api/documents` | Pobranie listy wszystkich przetworzonych dokumentów | `200` |
| `GET` | `/api/documents/{id}` | Pobranie szczegółów pojedynczego dokumentu wraz z chunkami | `200`, `404` |
| `GET` | `/api/documents/{id}/export` | Eksport chunków dokumentu do pliku (`?format=json` lub `?format=csv`) | `200`, `400`, `404` |

### Przykłady zapytań i odpowiedzi

#### 1. Przetwarzanie i segmentacja tekstu

**Żądanie (`POST /api/documents/process`):**

```json
{
  "text": "<h1>Architektura RAG</h1> Retrieval-Augmented Generation łączy <b>modele językowe</b> z zewnętrznymi bazami wiedzy.",
  "chunk_size": 4,
  "overlap": 1,
  "strategy": "word"
}
```

**Odpowiedź (`201 Created`):**

```json
{
  "id": 1,
  "original_text": "<h1>Architektura RAG</h1> Retrieval-Augmented Generation łączy <b>modele językowe</b> z zewnętrznymi bazami wiedzy.",
  "created_at": "2026-10-26T09:49:00",
  "chunks": [
    {
      "id": 1,
      "chunk_index": 0,
      "text": "Architektura RAG Retrieval-Augmented Generation",
      "token_count": 4
    },
    {
      "id": 2,
      "chunk_index": 1,
      "text": "Generation łączy modele językowe",
      "token_count": 4
    },
    {
      "id": 3,
      "chunk_index": 2,
      "text": "językowe z zewnętrznymi bazami",
      "token_count": 4
    },
    {
      "id": 4,
      "chunk_index": 3,
      "text": "bazami wiedzy.",
      "token_count": 2
    }
  ]
}
```

#### 2. Eksport danych

**Żądanie (`GET /api/documents/1/export?format=csv`):**

**Nagłówki odpowiedzi:**

- `Content-Type: text/csv; charset=utf-8`
- `Content-Disposition: attachment; filename=chunks_doc_1.csv`

**Treść odpowiedzi:**

```csv
chunk_index,token_count,text
0,4,Architektura RAG Retrieval-Augmented Generation
1,4,Generation łączy modele językowe
2,4,językowe z zewnętrznymi bazami
3,2,bazami wiedzy.
```

---
## Technologie użyte w projekcie

### Backend i API

- **Python 3.10+** — Główny język implementacji.
- **FastAPI** — Nowoczesny framework do tworzenia wydajnych interfejsów API w standardzie ASGI.
- **Uvicorn** — Serwer ASGI dla środowiska Python.
- **Pydantic v2** — Walidacja typów danych wejściowych i definicja schematów DTO.

### Baza danych i ORM

- **SQLite** — Relacyjny silnik bazy danych niewymagający zewnętrznego serwera.
- **SQLAlchemy 2.0** — Object-Relational Mapping (ORM) do zarządzania schematem i relacjami encji.

### Testowanie i jakość

- **Pytest** — Główny framework uruchamiania i parametryzacji testów.
- **HTTPX / FastAPI TestClient** — Klient do testowania endpointów API w izolacji.

### Frontend

- **HTML5 / CSS3** — Struktura wizualna aplikacji.
- **Bootstrap 5.3** — Responsywny framework interfejsu użytkownika.
- **JavaScript (Vanilla ES6)** — Asynchroniczna komunikacja z API (Fetch API) i dynamiczne renderowanie DOM.

