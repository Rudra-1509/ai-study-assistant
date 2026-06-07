# Implementation and Architecture

This document describes how AI Study Assistant is implemented, how requests move through the system, and how the frontend and backend modules fit together.

## 1. System Overview

AI Study Assistant has two main applications:

- **Frontend**: a React/Vite single-page app where users choose text, PDF, or image input and view generated study notes.
- **Backend**: a FastAPI service that extracts text, processes it through an NLP pipeline, calls an LLM, and returns topic-level study notes.

```mermaid
flowchart LR
    User[User] --> Browser[React/Vite frontend]
    Browser -->|multipart/form-data POST /analyze| API[FastAPI backend]
    API --> Ingestion[Input ingestion]
    Ingestion --> Pipeline[Study analysis pipeline]
    Pipeline --> LLM[LLM provider]
    LLM --> Pipeline
    Pipeline --> API
    API -->|StudyResponse JSON| Browser
    Browser --> Output[Markdown study notes]
```

## 2. Frontend Architecture

The frontend is organized around pages, components, hooks, an API client, and shared TypeScript types.

```mermaid
flowchart TD
    main[src/main.tsx] --> App[src/App.tsx]
    App --> Home[pages/Home.tsx]
    App --> Output[pages/Output.tsx]

    Home --> Header[components/Header.tsx]
    Home --> UploadSection[components/UploadSection.tsx]
    UploadSection --> UploadCard[components/UploadCard.tsx]
    UploadSection --> UseAnalyze[hooks/useAnalyze.ts]
    UseAnalyze --> AnalyzeAPI[api/analyze.ts]
    AnalyzeAPI --> Types[types/study.ts]

    Output --> TitleBar[components/TitleBar.tsx]
    Output --> ReactMarkdown[react-markdown]
    Output --> Types
```

### Frontend Flow

1. `App.tsx` defines two routes: `/` and `/output`.
2. `Home.tsx` renders the header and upload/input section.
3. `UploadSection.tsx` tracks the active input type, selected file, pasted text, loading state, and errors.
4. `UploadCard.tsx` handles PDF/image file selection through hidden file inputs.
5. `useAnalyze.ts` wraps the API call with loading/error state.
6. `api/analyze.ts` builds a `FormData` payload and posts it to `${VITE_API_URL}/analyze`.
7. On success, the app navigates to `/output` with the generated result in router state.
8. `Output.tsx` renders each topic's difficulty, keywords, and Markdown explanation.

```mermaid
sequenceDiagram
    actor U as User
    participant H as Home / UploadSection
    participant Hook as useAnalyze
    participant APIClient as api/analyze.ts
    participant Backend as FastAPI /analyze
    participant O as Output page

    U->>H: Select PDF/image or paste text
    H->>H: Lock other input modes
    U->>H: Click Generate Study Material
    H->>Hook: runAnalyze(input)
    Hook->>APIClient: analyze(input)
    APIClient->>Backend: POST multipart/form-data
    Backend-->>APIClient: StudyResponse JSON
    APIClient-->>Hook: result
    Hook-->>H: result
    H->>O: navigate('/output', { state: result })
    O->>O: Render topic cards and Markdown
```

## 3. Backend Architecture

The backend follows a staged pipeline. `api/main.py` owns HTTP concerns, while `controller.py` orchestrates the NLP and generation modules.

```mermaid
flowchart TD
    App[app.py] --> Uvicorn[uvicorn.run api.main:app]
    Uvicorn --> FastAPI[api/main.py FastAPI app]
    FastAPI --> Lifespan[Lifespan startup]
    Lifespan --> Semaphore[Initialize LLM semaphore]
    Lifespan --> Factory[llm/factory.py]
    Factory --> Cloudflare[llm/cloudfare.py]
    Factory --> Local[llm/local.py]

    FastAPI --> Analyze[POST /analyze]
    Analyze --> TextLoader[ingestion/text_loader.py]
    Analyze --> PDFLoader[ingestion/pdf_loader.py]
    Analyze --> ImgLoader[ingestion/img_loader.py]
    Analyze --> Controller[controller.py]

    Controller --> Cleaner[preprocessing/cleaner.py]
    Controller --> Chunker[preprocessing/chunker.py]
    Controller --> Embedder[embeddings/bert_embedder.py]
    Controller --> Classifier[understanding/topic_classifier.py]
    Controller --> Keywords[understanding/keyword_extractor.py]
    Controller --> Difficulty[understanding/difficulty_estimator.py]
    Controller --> Explainer[generation/explainer.py]
    Explainer --> LLMClient[LLM client]
    Controller --> Metrics[evaluation/metrics.py]
    Controller --> Logger[evaluation/logger.py]
```

## 4. Backend Request Lifecycle

```mermaid
sequenceDiagram
    participant Client as Frontend
    participant API as FastAPI /analyze
    participant Loader as Ingestion loader
    participant C as Controller
    participant E as Embedder
    participant U as Understanding modules
    participant G as Explainer
    participant L as LLM client
    participant M as Metrics/Logger

    Client->>API: POST /analyze(input_type, content/file)
    API->>API: Validate input_type and required fields
    API->>Loader: Extract text from text/PDF/image
    Loader-->>API: Raw text
    API->>C: run(text, llm_client)
    C->>C: Clean text and chunk text
    C->>E: Embed chunks
    E-->>C: Normalized vectors
    C->>U: Cluster topics, extract keywords, estimate difficulty
    U-->>C: topic_chunks, topic_keywords, difficulty
    C->>G: explain_all_topics(...)
    G->>L: Generate outline/content/conclusion prompts
    L-->>G: Generated text
    G-->>C: Topic explanations
    C->>M: Compute metrics and log run
    C-->>API: StudyResponse
    API-->>Client: JSON response
```

## 5. Input Ingestion

The `/analyze` endpoint accepts three input types.

```mermaid
flowchart TD
    Input{input_type}
    Input -->|text| Text[content form field]
    Text --> LoadText[load_text]
    LoadText --> RawText[Validated raw text]

    Input -->|pdf| PDF[file form field]
    PDF --> TempPDF[Write upload to temp file]
    TempPDF --> LoadPDF[load_pdf]
    LoadPDF --> PDFText{Page text length < 30?}
    PDFText -->|No| DirectText[Use PyMuPDF text]
    PDFText -->|Yes| OCRPage[Render page at 300 DPI and OCR]
    DirectText --> RawText
    OCRPage --> RawText

    Input -->|image| Image[file form field]
    Image --> TempImage[Write upload to temp file]
    TempImage --> LoadImage[load_img]
    LoadImage --> ImageOCR[Open image, grayscale, Tesseract OCR]
    ImageOCR --> RawText
```

### Loader Responsibilities

| Loader | Responsibility |
| --- | --- |
| `load_text` | Validate and trim pasted text. |
| `load_pdf` | Validate PDF extension, extract page text, OCR low-text pages. |
| `load_img` | Validate image extension and run Tesseract OCR. |

## 6. Analysis Pipeline

The controller is the central backend coordinator.

```mermaid
flowchart TD
    Raw[Raw extracted text]
    Raw --> Clean[clean_text]
    Clean --> Chunk[chunk_text]
    Chunk --> Embed[embed_text]
    Embed --> Cluster[topic_classifer / KMeans]
    Cluster --> Group[group_by_labels]
    Group --> Keyword[keyword_extractor]
    Group --> Difficulty[difficulty_estimator]
    Keyword --> Difficulty
    Group --> Explain[explain_all_topics]
    Keyword --> Explain
    Difficulty --> Explain
    Explain --> Metrics[compute_metrics]
    Metrics --> Log[log_run]
    Explain --> Response[StudyResponse]
```

### Stage Details

| Stage | Module | Implementation detail |
| --- | --- | --- |
| Cleaning | `preprocessing/cleaner.py` | Strips whitespace, normalizes hidden spaces, lowercases text. |
| Chunking | `preprocessing/chunker.py` | Groups paragraphs into chunks up to a default size of 800 characters. |
| Embedding | `embeddings/bert_embedder.py` | Loads `sentence-transformers/all-MiniLM-L6-v2` once and encodes chunks in batches. |
| Topic clustering | `understanding/topic_classifier.py` | Uses KMeans; cluster count scales with the number of chunks. |
| Grouping | `understanding/keyword_extractor.py` | Maps cluster labels to chunk lists. |
| Keyword extraction | `understanding/keyword_extractor.py` | Removes stopwords, filters short words, ranks by frequency. |
| Difficulty estimation | `understanding/difficulty_estimator.py` | Scores keyword length, average chunk length, and topic breadth. |
| Generation | `generation/explainer.py` | Builds outlines, selects section context, prompts the LLM, deduplicates content, and returns Markdown. |
| Evaluation | `evaluation/metrics.py` | Measures word count, keyword coverage, and expected length fit. |
| Logging | `evaluation/logger.py` | Appends summary metrics to `run_logs.jsonl`. |

## 7. Topic Clustering Strategy

The topic classifier chooses the number of clusters from the number of chunks.

```mermaid
flowchart TD
    N[Number of chunks]
    N --> A{N <= 5?}
    A -->|Yes| K1[k = 1]
    A -->|No| B{N <= 12?}
    B -->|Yes| K2[k = 2]
    B -->|No| C{N <= 25?}
    C -->|Yes| K3[k = 3]
    C -->|No| K5[k = 5]
    K1 --> KM[KMeans]
    K2 --> KM
    K3 --> KM
    K5 --> KM
    KM --> Labels[Topic labels per chunk]
```

## 8. Difficulty Estimation

Difficulty is heuristic rather than model-generated. For each topic:

```mermaid
flowchart TD
    Topic[Topic chunks + keywords]
    Topic --> F1[Keyword complexity: average keyword length / 10]
    Topic --> F2[Cognitive load: average words per chunk / 100]
    Topic --> F3[Topic breadth: chunk count / 5]
    F1 --> Score[total_score]
    F2 --> Score
    F3 --> Score
    Score --> Easy{score < 1.5?}
    Easy -->|Yes| E[easy]
    Easy -->|No| Medium{score < 3?}
    Medium -->|Yes| M[medium]
    Medium -->|No| H[hard]
```

## 9. LLM Provider Architecture

The LLM layer is designed around a common client abstraction and a factory.

```mermaid
classDiagram
    class LLMClient {
        <<abstract>>
        generate(prompt)
    }

    class CloudflareLLMClient {
        api_token
        account_id
        model
        client
        url
        headers
        generate(prompt, max_tokens)
        close()
    }

    class LocalLLMClient {
        model_dir
        model_file
        llm
        generate(prompt)
    }

    LLMClient <|-- CloudflareLLMClient
    LLMClient <|-- LocalLLMClient

    class Factory {
        get_llm_client()
    }

    Factory --> CloudflareLLMClient
    Factory --> LocalLLMClient
```

### Provider Selection

```mermaid
flowchart TD
    Env[LLM_PROVIDER env var]
    Env --> Provider{provider}
    Provider -->|cloudflare or unset| CF[CloudflareLLMClient]
    Provider -->|local| Local[LocalLLMClient]
    Provider -->|unknown| Error[ValueError]
```

The FastAPI lifespan initializes one shared LLM client and stores it on `app.state.llm_client`. It also initializes a global semaphore in the explainer module to limit concurrent LLM calls.

## 10. Explanation Generation

The explainer is the most detailed part of the backend. It generates notes topic by topic and section by section.

```mermaid
flowchart TD
    TopicInput[Topic chunks, keywords, difficulty]
    TopicInput --> Dedupe[Deduplicate chunks]
    Dedupe --> Outline[Generate section outline]
    Outline --> HeaderDedupe[Remove overlapping headers]
    HeaderDedupe --> Cap[Cap section count by difficulty and chunk count]
    Cap --> Context[Select context per header]
    Context --> GenerateSections[Generate section content]
    GenerateSections --> FactDedupe[Deduplicate facts across sections]
    FactDedupe --> SimilarDedupe[Remove similar sections]
    SimilarDedupe --> SparseFilter[Drop sparse sections]
    SparseFilter --> Conclusion[Generate conclusion]
    Conclusion --> Markdown[Assemble Markdown explanation]
```

### Generation Substeps

1. **Chunk deduplication** removes repeated source chunks.
2. **Outline generation** asks the LLM for mutually exclusive Markdown section headers.
3. **Header cleanup** removes overlapping headers and guarantees a conclusion section.
4. **Section count capping** adapts the maximum number of body sections to topic difficulty.
5. **Context selection** scores chunks against each header, keywords, semantic hints, and reuse penalties.
6. **Section generation** prompts the LLM to write only facts explicitly found in the selected context.
7. **Pair-safe post-processing** keeps headers and generated content aligned while removing duplicate facts and sparse sections.
8. **Conclusion generation** summarizes the actually retained sections.
9. **Markdown assembly** returns the final topic explanation.

## 11. Response Contract

The backend returns a record keyed by topic label. Each topic includes difficulty, keywords, and a Markdown explanation.

```mermaid
classDiagram
    class StudyResponse {
        object topicsByLabel
    }

    class TopicResult {
        Difficulty difficulty
        string[] keywords
        string explanation
    }

    class Difficulty {
        <<enumeration>>
        easy
        medium
        hard
    }

    StudyResponse --> TopicResult
    TopicResult --> Difficulty
```

Example:

```json
{
  "0": {
    "difficulty": "easy",
    "keywords": ["graph", "nodes", "edges"],
    "explanation": "## Nodes and Edges\n...\n\n## Conclusion\n..."
  }
}
```

## 12. Evaluation and Logging

After generation, the backend computes lightweight quality metrics.

```mermaid
flowchart TD
    Explanation[Generated explanations]
    Explanation --> PerTopic[Per-topic metrics]
    PerTopic --> WordCount[Word count]
    PerTopic --> Coverage[Keyword coverage]
    PerTopic --> LengthFit[Expected length fit by difficulty]
    WordCount --> Summary[Summary metrics]
    Coverage --> Summary
    Summary --> LogEntry[JSONL log entry]
    LogEntry --> RunLogs[run_logs.jsonl]
```

Logged fields include:

- UTC timestamp
- input length in characters
- number of topics
- metrics summary

## 13. Error Handling

```mermaid
flowchart TD
    Request[POST /analyze]
    Request --> Validate[Validate input_type and required data]
    Validate --> BadRequest{Invalid?}
    BadRequest -->|Yes| HTTP400[HTTP 400]
    BadRequest -->|No| Process[Process request]
    Process --> Exception{Unhandled exception?}
    Exception -->|Yes| Trace[Print traceback]
    Trace --> HTTP500[HTTP 500 with error detail]
    Exception -->|No| OK[HTTP 200 StudyResponse]
```

The API raises `HTTPException` for invalid input and catches unexpected errors to return a 500 response with diagnostic detail.

## 14. Important Implementation Notes

- Backend startup happens in the FastAPI lifespan hook, which initializes both the LLM semaphore and shared LLM client.
- Uploaded files are written to temporary files because the PDF and image loaders operate on filesystem paths.
- Temporary upload files are deleted in a `finally` block after extraction.
- Topic labels are generated by KMeans and are not stable semantic names.
- The frontend stores the response in React Router navigation state; refreshing `/output` without state redirects back to `/`.
- The Cloudflare LLM client is asynchronous and includes a `close()` method for FastAPI shutdown.
- The generation pipeline defaults to sequential section generation within each topic to reduce repeated facts.

## 15. Opportunities for Improvement

- Add human-readable topic titles separate from numeric cluster labels.
- Fix text normalization regexes so OCR whitespace cleanup uses `\n+` and `\s+` patterns instead of literal slash patterns.
- Make the local LLM client async-compatible with the Cloudflare client signature.
- Add source-grounded citations from chunks to generated sections.
- Improve keyword extraction with n-grams or TF-IDF.
- Persist analysis jobs and output instead of passing results only through router state.
- Add automated backend tests and frontend component tests.
- Add production CORS and deployment-specific environment configuration.
