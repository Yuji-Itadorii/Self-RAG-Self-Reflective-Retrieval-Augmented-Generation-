from app.config import Settings


def test_config_defaults():
    settings = Settings()

    assert settings.generation_model == "gpt-4o"
    assert settings.critique_model == "gpt-4o-mini"
    assert settings.embedding_model == "text-embedding-3-small"

    assert isinstance(settings.embedding_dimension, int)
    assert settings.embedding_dimension == 1536

    assert settings.retrieval_top_k > 0
    assert settings.max_revisions > 0
    assert settings.max_rewrites > 0

    assert 0 <= settings.relevance_threshold <= 1
    assert 0 <= settings.support_threshold <= 1
    assert 0 <= settings.usefulness_threshold <= 1


def test_loop_caps_are_positive():
    settings = Settings()
    assert settings.max_revisions > 0
    assert settings.max_rewrites > 0


def test_model_names_non_empty():
    settings = Settings()
    assert len(settings.generation_model) > 0
    assert len(settings.critique_model) > 0
    assert len(settings.embedding_model) > 0
