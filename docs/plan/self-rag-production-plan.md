# Self-RAG: Production-Grade Build Plan (From Scratch)

## 1. Goal

Build a Self-RAG system from scratch with LangGraph, designed from day one around **production practices**: observability, evaluation, memory, CI gating, and cost control. The README headline is a before/after metrics table, not a list of integrations.

**Target headline claims (fill in with measured numbers):**

- Self-RAG improves faithfulness from `__%` (vanilla RAG) to `__%` on an ~80-example golden set.
- Routing critique nodes to a small model cuts per-query cost by `__%` with no regression on the eval set.
- Prompt and node changes are gated by an automated eval suite in CI.

---

## 2. Starting Point and Design Decisions

Nothing is built yet. The target graph (from the design diagram) has these nodes: `decide_retrieval`, `retrieve`, `is_relevant`, `generate_from_context`, `is_supported`, `revise_answer`, `is_use`, `rewrite_question`, `generate_direct`, `no_answer_found`.

Because the project starts clean, build these in from the start instead of retrofitting them:

- **Loop caps in state** (`revision_count`, `rewrite_count`), not just `recursion_limit`
- **Structured outputs** (Pydantic + enum literals) on all critique nodes
- **Per-document relevance grading**, run in parallel
- **`rewrite_question` loops back to `retrieve`**, and zero relevant docs tries one rewrite before `no_answer_found`
- **`generate_direct` goes through a check** (at minimum `is_use`) before End
- **pgvector from the start**, so there is no FAISS-to-Postgres migration later
- **Small model for critique nodes, large model for generation**, configurable per node from the start so the cost experiment is a config change

Decisions to make in Phase 0: corpus/domain, LLM provider and model pair (small + large), embedding model, Python tooling.

---

## 3. Phases

### Phase 0: Project setup and foundations

- [x] Create repo, Python environment (uv or poetry), `ruff`, `pytest`, pre-commit
- [x] Config module: model names per node, thresholds, loop caps, all via env/settings
- [x] `docker-compose.yml` with Postgres + pgvector
- [x] Choose the corpus (a domain you can write good questions about; 50-200 documents is plenty)
- [x] Choose the model pair (small for critique, large for generation) and embedding model
- [x] Set up secrets handling (`.env.example`, nothing committed)

**Exit criteria:** `docker compose up` starts the database; tests and linter run in one command.

### Phase 1: Corpus, ingestion, and vanilla RAG baseline

- [ ] Ingestion pipeline: load, clean, chunk, embed, store in pgvector with metadata
- [ ] Retrieval function with top-k and metadata filtering
- [ ] **Vanilla RAG baseline** (retrieve then generate, no critique nodes), kept as a permanent comparison point
- [ ] Start drafting golden-dataset questions while you read the corpus (finish in Phase 4)

**Exit criteria:** baseline answers questions over your corpus end to end; re-ingestion is a single command.

### Phase 2: Build the Self-RAG graph

Build incrementally rather than all at once.

- [ ] Define the state schema (question, documents, answer, verdicts, counters, history placeholder)
- [ ] Skeleton graph with stub nodes and all edges wired, so routing is testable before any LLM call
- [ ] Implement nodes in this order: `decide_retrieval`, `generate_direct`, `retrieve`, `is_relevant`, `generate_from_context`, `is_supported`, `revise_answer`, `is_use`, `rewrite_question`, `no_answer_found`
- [ ] Per-document relevance grading with parallel fan-out; filter to relevant subset, branch on survivors
- [ ] Enforce loop caps; fall through to `no_answer_found` when exceeded
- [ ] Unit tests for every routing function and for each grader's schema validation
- [ ] Render the compiled graph and compare against the design diagram

**Exit criteria:** the graph runs end to end on all four paths (answer, direct, rewrite, no-answer); no unbounded loops; routing tested.

### Phase 3: Observability (LangSmith)

- [ ] Enable tracing via env vars
- [ ] Tag runs with `thread_id`, `user_id`, and routing decisions as metadata
- [ ] Record token count, latency, and cost per node
- [ ] Add a feedback endpoint (thumbs up/down) that writes back to LangSmith runs
- [ ] Note alternatives considered (Langfuse, Arize Phoenix) and why LangSmith was chosen

**Exit criteria:** can filter traces by path taken (e.g., "rewrite path", "failed `is_supported` twice") and see cost per node.

### Phase 4: Evaluation harness (highest-value phase)

- [ ] Finish golden dataset (~80 examples) across four buckets:
  - Answerable from corpus
  - Not answerable from corpus (should reach `no_answer_found`)
  - General knowledge (should route to `generate_direct`)
  - Ambiguous or poorly phrased (should trigger `rewrite_question`)
- [ ] Node-level evaluators: routing accuracy; grader agreement with human labels
- [ ] End-to-end evaluators: faithfulness, answer correctness, retrieval recall@k
- [ ] Run vanilla RAG baseline and Self-RAG on the same dataset
- [ ] Produce a results table: vanilla RAG vs Self-RAG
- [ ] Iterate on prompts using eval results, recording what changed and the metric delta

**Exit criteria:** one command runs the full eval and outputs the comparison table.

### Phase 5: Memory

- [ ] Thread memory: LangGraph checkpointer (`MemorySaver` first, then Postgres)
- [ ] Cross-thread memory: LangGraph store, namespaced per user, with semantic recall
- [ ] `decide_retrieval` and `rewrite_question` read the last N turns (coreference like "what about its pricing?")
- [ ] Summarization node that compacts history past a token threshold
- [ ] Add multi-turn examples to the golden dataset

**Exit criteria:** follow-up questions resolve correctly; conversations survive a process restart.

### Phase 6: CI gate

- [ ] GitHub Actions workflow running an eval subset on PRs touching prompts or nodes
- [ ] Post the metrics table as a PR comment
- [ ] Fail the build if faithfulness drops below threshold
- [ ] Store prompts as versioned files; attach prompt hash to traces

**Exit criteria:** a deliberately bad prompt change fails CI (keep this PR as a demo).

### Phase 7: Cost and serving

- [ ] Run the cost experiment: critique nodes on small model vs large model, rerun evals, record the delta
- [ ] Semantic cache for repeated queries
- [ ] Retries with backoff, timeouts, fallback model
- [ ] Document the reindex process and metadata filtering
- [ ] FastAPI service with SSE streaming and a health check
- [ ] Mitigation notes for prompt injection via retrieved documents
- [ ] Containerize the app alongside the database in `docker-compose.yml`

**Exit criteria:** measured cost reduction with no eval regression; the whole service runs via `docker compose up`.

---

## 4. Suggested Repo Structure

```
self-rag/
├── app/
│   ├── config.py       # per-node models, thresholds, loop caps
│   ├── graph/          # state, nodes, edges, routing
│   ├── prompts/        # versioned prompt files
│   ├── retrieval/      # ingestion, vector store
│   ├── memory/         # checkpointer, store, summarizer
│   └── api/            # FastAPI service
├── evals/
│   ├── datasets/       # golden set (4 buckets)
│   ├── evaluators/     # node-level + end-to-end
│   └── baseline/       # vanilla RAG
├── tests/
├── .github/workflows/  # eval gate
├── docker-compose.yml
└── README.md
```

---

## 5. Rough Timeline (part-time estimate, adjust to your pace)

| Phase | Effort |
|---|---|
| 0. Setup | 2-3 days |
| 1. Ingestion + baseline | 4-5 days |
| 2. Self-RAG graph | 1-1.5 weeks |
| 3. Observability | 2-3 days |
| 4. Evals | 1-1.5 weeks |
| 5. Memory | 4-5 days |
| 6. CI gate | 2-3 days |
| 7. Cost + serving | 1 week |

Total: roughly 6-8 weeks part-time.

---

## 6. Priorities If Time-Boxed

1. **Phases 0-2** (nothing works without these)
2. **Phase 4** (golden dataset, node-level evals, baseline comparison)
3. **Phase 7**, cost-routing experiment only

Phases 3, 5, and 6 follow. The serving work in Phase 7 is stretch.

---

## 7. Explicitly Out of Scope

Harness.io, Kubernetes, a polished frontend, multi-agent layers, and extra integrations added for logo count.

---

## 8. README Outline

1. One-paragraph problem statement
2. Architecture diagram
3. **Results table** (vanilla RAG vs Self-RAG: faithfulness, correctness, latency, cost)
4. Cost optimization experiment
5. Eval methodology and dataset design
6. Observability screenshots (trace with routing metadata)
7. CI gate demo (failing PR)
8. Known limitations and what still doesn't work
9. How to run
