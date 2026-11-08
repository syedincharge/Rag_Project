# Rag_Project

A hands-on walkthrough of production-shaped **Retrieval-Augmented Generation** patterns, built with
LangChain and Qdrant over a small synthetic helpdesk knowledge base.

Everything lives in a single annotated notebook, [`main.ipynb`](main.ipynb), which starts from raw
documents in half a dozen formats and works up to hybrid retrieval with query transformation.

## What it covers

**Ingestion** — loading CSV, PDF, DOCX, Markdown, HTML, Python source, and JSON into a single
document set, each tagged with metadata for later filtering.

**Chunking strategies**, compared side by side on the same page:

| Strategy | Approach |
| --- | --- |
| Fixed-length | `RecursiveCharacterTextSplitter`, uniform character windows |
| Structure-aware | `MarkdownHeaderTextSplitter`, splits on heading hierarchy |
| Semantic | embedding-distance boundaries at a percentile cutoff |

**Indexing** — versioned Qdrant collections (`helpdesk_production_v1` / `v2`) behind a stable
`helpdesk_live` alias, so an index can be rebuilt and swapped atomically. Chunk IDs are
`uuid5`-derived from source plus content hash, making re-indexing idempotent rather than
duplicative. Payload indexes are created for every filterable field.

**Retrieval** — dense, sparse (BM25 via FastEmbed), and hybrid with server-side Reciprocal Rank
Fusion, plus tenant and status access filters applied on every query.

**Metadata filtering** — business filters validated against allowlists derived from the corpus, so
an unknown or injected filter value is rejected rather than passed through to the store.

**Advanced retrieval**

- Contextual retrieval — each chunk prefixed with an LLM-written sentence situating it in its source
- Parent-document retrieval — search small chunks, return the larger parent for context
- Multi-vector retrieval — multiple embeddings per logical document

**Query intelligence**

- Query rewriting into standalone search queries
- Multi-query expansion fused with RRF
- HyDE — embedding a hypothetical answer as the search probe
- Self-query — structured extraction of query plus metadata filters, allowlist-validated
- Query routing

## Requirements

- **Python ≥ 3.14**
- **[uv](https://docs.astral.sh/uv/)** for dependency management
- **A running Qdrant instance** reachable at `QDRANT_URL`
- **An [OpenRouter](https://openrouter.ai) API key**

## Setup

**1. Install dependencies**

```bash
uv sync
```

**2. Configure credentials**

```bash
cp .env.example .env
```

Then edit `.env` and set `OPENROUTER_API_KEY`. See [`.env.example`](.env.example) for every
supported variable. `.env` is gitignored — never commit it.

> If `OPENROUTER_API_KEY` is not set in the environment, the notebook's first cell prompts for it
> via `getpass`, so the key is never written into the notebook.

**3. Start Qdrant**

```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

**4. Run the notebook**

The project ships `ipykernel`, so open `main.ipynb` in your IDE (PyCharm, VS Code) and select the
`.venv` interpreter. To run it in a browser instead, add a frontend first:

```bash
uv add --dev jupyterlab
uv run jupyter lab main.ipynb
```

Run the cells top to bottom — later cells depend on names defined earlier. If you restart the
kernel, re-run from the top rather than jumping to the middle.

## Knowledge base

The corpus under `src/knowledge/` is synthetic sample data, deliberately spanning several formats so
the loaders and chunkers have something realistic to chew on:

```text
src/knowledge/
├── catalog/plans.json              # structured product catalog
├── faq/support_faq.csv             # 63 Q&A rows, one Document each
├── policies/
│   ├── employee_handbook.pdf       # 8 pages
│   ├── expense_policy.pdf          # 5 pages
│   └── travel_memo.docx
├── scans/vendor_contract.pdf       # scanned PDF, not loaded by the notebook
└── wiki/
    ├── holiday_calendar.html
    ├── onboarding.md               # heading-rich, used for chunking demos
    ├── payments_runbook.md         # used for contextual retrieval
    └── retry_helper.py
```

A full ingest produces **82 source documents → 135 chunks**.

`scans/vendor_contract.pdf` is a text-layer-free scan included as raw material for an OCR pass; no
cell currently loads it.

## Notes on cost

The notebook makes roughly **21 LLM requests** per complete pass — 16 of them in the contextual
retrieval cell, which contextualizes each runbook chunk individually.

OpenRouter's free tier allows **50 model requests per day**, so a full run costs a meaningful slice
of the daily allowance. To make iteration practical, responses are cached on disk:

```python
set_llm_cache(SQLiteCache(database_path=".langchain_cache.sqlite"))
```

Re-running a cell whose prompts have not changed costs **zero** new requests. Delete
`.langchain_cache.sqlite` to force fresh calls. The cache file is gitignored.

If you hit `429 free-models-per-day`, the quota is exhausted — retries will not help, since it is a
daily limit rather than a burst limit. Wait for the UTC-midnight reset or add credits.

## Development

Notebook outputs are stripped from commits to keep diffs readable and avoid committing response
data. [`nbstripout`](https://github.com/kynan/nbstripout) is included as a dev dependency:

```bash
uv run nbstripout --install
```

This installs a git filter that clears outputs automatically on every commit.

## Repository layout

```text
.
├── main.ipynb          # the walkthrough — all of the work lives here
├── main.py             # IDE scaffold, not used by the notebook
├── pyproject.toml      # dependencies (uv)
├── .env.example        # template for required environment variables
└── src/
    ├── knowledge/      # sample corpus
    └── rag_project/    # package scaffold
```
