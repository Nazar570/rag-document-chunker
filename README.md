# Testowanie i Jakość Oprogramowania II

## Autor

Nazar Suslyk

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
   git clone https://github.com/Nazar570/rag-document-chunker
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

Projekt posiada kompleksowy zestaw 41 zautomatyzowanych testów (29 jednostkowych oraz 12 integracyjnych) zorganizowanych według standardu **AAA (Arrange-Act-Assert)**:

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

## Przypadki testowe dla testera manualnego (TestCase)

Poniższe scenariusze testowe zostały przygotowane dla testera manualnego w celu weryfikacji poprawności działania interfejsu graficznego (UI), walidacji formularzy, silnika czyszczenia tekstu, algorytmów podziału, generowania plików eksportu oraz integracji z API.

---

| ID | TC001 |
| :--- | :--- |
| Tytuł | Weryfikacja poprawnego podziału tekstu według słów z parametrem overlap |
| Warunki początkowe | Aplikacja jest uruchomiona pod adresem `http://127.0.0.1:8000/`, strona główna jest załadowana w przeglądarce, pola formularza zawierają wartości domyślne. |
| Kroki testowe | 1. W polu tekstowym „Input text” wpisz: `jeden dwa trzy cztery pięć sześć`.<br>2. W polu „Chunk Size” wprowadź wartość `3`.<br>3. W polu „Overlap” wprowadź wartość `1`.<br>4. W liście rozwijanej „Strategy” wybierz opcję `By words`.<br>5. Kliknij przycisk „Split into chunks”. |
| Oczekiwany rezultat | Pod formularzem pojawia się sekcja „Generated chunks” z dwoma kafelkami:<br>• Chunk #0 z tekstem `jeden dwa trzy` oraz etykietą `Units: 3`.<br>• Chunk #1 z tekstem `trzy cztery pięć` oraz etykietą `Units: 3`.<br>Komunikat o błędzie nie jest widoczny. |

---

| ID | TC002 |
| :--- | :--- |
| Tytuł | Weryfikacja segmentacji według liczby znaków |
| Warunki początkowe | Strona główna `http://127.0.0.1:8000/` jest załadowana w przeglądarce. |
| Kroki testowe | 1. W polu „Input text” wpisz ciąg znaków: `ABCDEFGHIJ`.<br>2. W polu „Chunk Size” wprowadź wartość `4`.<br>3. W polu „Overlap” wprowadź wartość `1`.<br>4. W liście rozwijanej „Strategy” wybierz opcję `By characters`.<br>5. Kliknij przycisk „Split into chunks”. |
| Oczekiwany rezultat | Na liście wygenerowanych fragmentów pojawiają się 3 kafelki:<br>• Chunk #0: `ABCD` (Units: 4)<br>• Chunk #1: `DEFG` (Units: 4)<br>• Chunk #2: `GHIJ` (Units: 4) |

---

| ID | TC003 |
| :--- | :--- |
| Tytuł | Weryfikacja usuwania tagów HTML i formatowania Markdown przed podziałem tekstu |
| Warunki początkowe | Strona główna aplikacji jest otwarta. |
| Kroki testowe | 1. W polu „Input text” wpisz: `<h3>Tytuł sekcji</h3> To jest [artykuł](https://example.com) oraz <b>ważna informacja</b>`.<br>2. Ustaw „Chunk Size” na `10`, „Overlap” na `0`, „Strategy” na `By words`.<br>3. Kliknij przycisk „Split into chunks”. |
| Oczekiwany rezultat | Wygenerowany chunk nie zawiera znaczników `<h3>`, `</h3>`, `<b>`, `</b>` ani składni linku Markdown `[...] (...)`. Widoczny tekst to: `Tytuł sekcji To jest artykuł oraz ważna informacja.`. |

---

| ID | TC004 |
| :--- | :--- |
| Tytuł | Weryfikacja blokady nieprawidłowej relacji parametrów chunk_size i overlap |
| Warunki początkowe | Strona główna aplikacji jest otwarta. |
| Kroki testowe | 1. W polu „Input text” wpisz: `Przykładowy tekst do przetworzenia`.<br>2. W polu „Chunk Size” wprowadź `4`.<br>3. W polu „Overlap” wprowadź `4` (wartość równa rozmiarowi chunka).<br>4. Kliknij przycisk „Split into chunks”. |
| Oczekiwany rezultat | Na ekranie pojawia się czerwony baner z komunikatem błędu: `overlap must be smaller than chunk_size`. Lista wygenerowanych chunków nie zostaje wyświetlona. |

---

| ID | TC005 |
| :--- | :--- |
| Tytuł | Obsługa tekstu zawierającego wyłącznie białe znaki i puste tagi HTML |
| Warunki początkowe | Strona główna aplikacji jest otwarta. |
| Kroki testowe | 1. W polu „Input text” wprowadź ciąg złożony wyłącznie z tagów i spacji: `<div>   <p> </p>  </div>`.<br>2. Kliknij przycisk „Split into chunks”. |
| Oczekiwany rezultat | Wyświetla się czerwony baner błędu z informacją: `text cannot be empty after cleaning`. Żaden dokument nie zostaje dodany do bazy danych. |

---

| ID | TC006 |
| :--- | :--- |
| Tytuł | Podział tekstu o długości mniejszej niż zadany Chunk Size |
| Warunki początkowe | Strona główna aplikacji jest otwarta. |
| Kroki testowe | 1. W polu „Input text” wpisz: `Krótka fraza`.<br>2. W polu „Chunk Size” wprowadź `10`.<br>3. W polu „Overlap” wprowadź `2`.<br>4. Wybierz strategię `By words`.<br>5. Kliknij przycisk „Split into chunks”. |
| Oczekiwany rezultat | System tworzy dokładnie jeden kafelek (Chunk #0) zawierający pełny tekst `Krótka fraza` z etykietą `Units: 2`. |

---

| ID | TC007 |
| :--- | :--- |
| Tytuł | Weryfikacja poprawnego pobierania pliku JSON po przetworzeniu dokumentu |
| Warunki początkowe | Strona główna aplikacji jest otwarta, wykonano uprzednio podział dowolnego tekstu (np. z TC001) i widoczne są przyciski eksportu. |
| Kroki testowe | 1. W sekcji „Generated chunks” kliknij przycisk „Export JSON”.<br>2. Sprawdź plik pobrany przez przeglądarkę w folderze Pobrane (Downloads).<br>3. Otwórz pobrany plik w edytorze tekstu. |
| Oczekiwany rezultat | • Przeglądarka pobiera plik o nazwie `chunks_doc_<ID>.json`.<br>• Plik zawiera poprawną składnię tablicy obiektów JSON z kluczami `chunk_index`, `text`, `token_count`.<br>• Polskie znaki diakrytyczne są zachowane w czytelnej postaci (UTF-8). |

---

| ID | TC008 |
| :--- | :--- |
| Tytuł | Weryfikacja eksportu chunków do formatu arkusza kalkulacyjnego CSV |
| Warunki początkowe | Na stronie widoczne są wygenerowane chunki z aktywnego formularza. |
| Kroki testowe | 1. W sekcji „Generated chunks” kliknij przycisk „Export CSV”.<br>2. Otwórz pobrany plik w programie Excel lub notatniku. |
| Oczekiwany rezultat | • Przeglądarka pobiera plik o nazwie `chunks_doc_<ID>.csv`.<br>• Pierwszy wiersz pliku to nagłówek kolumn: `chunk_index,token_count,text`.<br>• Kolejne wiersze zawierają dane liczbowe i tekstowe oddzielone przecinkami zgodnie ze specyfikacją CSV. |

---

| ID | TC009 |
| :--- | :--- |
| Tytuł | Potwierdzenie zapisu encji dokumentu i powiązanych chunków w bazie SQLite |
| Warunki początkowe | Przetworzono co najmniej jeden dokument w interfejsie graficznym. |
| Kroki testowe | 1. Otwórz nową kartę przeglądarki pod adresem `http://127.0.0.1:8000/docs`.<br>2. Rozwiń sekcję `GET /api/documents`.<br>3. Kliknij przycisk „Try it out”, a następnie „Execute”.<br>4. Zweryfikuj pole „Server response”. |
| Oczekiwany rezultat | Serwer zwraca kod odpowiedzi `200 OK`. W ciele odpowiedzi znajduje się tablica dokumentów w formacie JSON z unikalnymi identyfikatorami `id`, znacznikiem czasu `created_at` oraz zagnieżdżoną listą obiektów `chunks`. |

---

| ID | TC010 |
| :--- | :--- |
| Tytuł | Weryfikacja ograniczeń atrybutów min pól formularza numerycznego |
| Warunki początkowe | Strona główna aplikacji jest otwarta. |
| Kroki testowe | 1. Wpisz dowolny tekst w polu „Input text”.<br>2. W polu „Chunk Size” spróbuj wprowadzić wartość `0` lub `-1`.<br>3. W polu „Overlap” spróbuj wprowadzić `-1`.<br>4. Kliknij przycisk „Split into chunks”. |
| Oczekiwany rezultat | Wbudowany mechanizm walidacji przeglądarki (HTML5 constraint validation) blokuje wysłanie formularza, podświetlając pole i wyświetlając dymek informujący, że wartość musi być większa lub równa minimalnemu limitowi (`min="1"` dla Chunk Size, `min="0"` dla Overlap). Żadne zapytanie sieciowe nie zostaje wysłane. |


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

