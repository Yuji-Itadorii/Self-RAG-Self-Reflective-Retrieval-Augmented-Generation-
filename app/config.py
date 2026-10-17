# app/config.py
"""
Configuration module for the Self-RAG system.

This module defines the application settings using pydantic-settings.
It supports loading configuration from environment variables and `.env` files.
Settings are cached using `lru_cache` to prevent multiple readings of environment variables
during runtime, ensuring fast and consistent configuration access.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings and configuration parameters.

    Attributes can be overridden by environment variables prefixed with `SELFRAG_`.
    For example, `SELFRAG_GENERATION_MODEL=gpt-4` would override `generation_model`.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="SELFRAG_",
        case_sensitive=False,
    )

    # --- LLM Models ---
    generation_model: str = Field(
        default="gpt-4o",
        description="Large model used for answer generation nodes",
    )
    critique_model: str = Field(
        default="gpt-4o-mini",
        description="Small model for critique/grading nodes (is_relevant, is_supported, is_use)",
    )
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Embedding model for document vectors",
    )
    embedding_dimension: int = Field(
        default=1536,
        description="Dimension of embedding vectors",
    )

    # --- Retrieval ---
    retrieval_top_k: int = Field(
        default=5,
        description="Number of documents to retrieve",
    )

    # --- Grading Thresholds ---
    relevance_threshold: float = Field(
        default=0.7,
        description="Minimum score for a document to be considered relevant",
    )
    support_threshold: float = Field(
        default=0.7,
        description="Minimum score for an answer to be considered supported by context",
    )
    usefulness_threshold: float = Field(
        default=0.5,
        description="Minimum score for an answer to be considered useful",
    )

    # --- Loop Caps ---
    max_revisions: int = Field(
        default=2,
        description="Maximum number of answer revision attempts",
        gt=0,
    )
    max_rewrites: int = Field(
        default=2,
        description="Maximum number of question rewrite attempts",
        gt=0,
    )

    # --- Chunking ---
    chunk_size: int = Field(
        default=1000,
        description="Document chunk size in characters",
    )
    chunk_overlap: int = Field(
        default=200,
        description="Overlap between document chunks in characters",
    )

    # --- Database ---
    database_url: str = Field(
        default="postgresql://selfrag:selfrag@localhost:5432/selfrag",
        description="PostgreSQL connection string (pgvector)",
    )
    collection_name: str = Field(
        default="selfrag_documents",
        description="Name of the pgvector collection/table",
    )

    # --- Observability ---
    langsmith_project: str = Field(
        default="self-rag",
        description="LangSmith project name for tracing",
    )

    # --- API Keys (no defaults — must be provided) ---
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key",
    )
    langsmith_api_key: str = Field(
        default="",
        description="LangSmith API key",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    This function should be used to access settings throughout the application.
    Call .cache_clear() in tests if you need to reset the configuration.
    """
    return Settings()
