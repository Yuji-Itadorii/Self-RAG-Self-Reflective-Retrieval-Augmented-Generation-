# Phase 0 Architecture and Technology Decisions

This document outlines the foundational technology choices made during Phase 0 of the Self-RAG project.

## Decisions

- **Package manager**: `uv`
  - *Rationale*: Blazing fast, modern package manager built in Rust. It replaces pip, pip-tools, and poetry for dependency management, significantly speeding up environment creation and resolution.

- **Linter/formatter**: `ruff`
  - *Rationale*: An extremely fast Python linter and code formatter written in Rust. It effectively replaces flake8, isort, and black in a single tool, simplifying the development workflow and CI/CD pipelines.

- **Config**: `pydantic-settings`
  - *Rationale*: Provides highly robust, typed, and validated configuration management based on environment variables. It reduces boilerplate code and ensures the application fails fast if critical configuration is missing or invalid.

- **Database**: PostgreSQL + pgvector
  - *Rationale*: A production-grade vector store setup. Using pgvector inside PostgreSQL provides immediate robustness, relational data capabilities alongside vector similarity search, and eliminates the need for migrating from a lightweight solution (like FAISS) later in the project lifecycle.

- **Model pair**: GPT-4o (generation) + GPT-4o-mini (critique)
  - *Rationale*: Cost optimization from day one. Generating high-quality responses benefits from the advanced reasoning of GPT-4o, while the intermediate critique nodes (relevance, faithfulness) are simpler classification tasks that do not require the large model's capabilities, making GPT-4o-mini an ideal, cost-effective choice.

- **Embedding model**: `text-embedding-3-small`
  - *Rationale*: Provides an excellent balance of embedding quality, speed, and cost. Its 1536-dimensional outputs integrate perfectly with standard pgvector configurations while keeping latency low.

- **Corpus**: *To be decided (Phase 1)*
  - *Rationale*: The specific document corpus for retrieval is still open and will be evaluated and integrated in the next development phase.

- **Testing**: `pytest`
  - *Rationale*: The industry standard for Python testing. We also utilize `pytest-asyncio` to natively test asynchronous LangGraph nodes and workflows.

- **Pre-commit**: `ruff` hooks
  - *Rationale*: Enforces code quality and formatting standards automatically upon commit, catching issues early before they reach Continuous Integration.
