from app.core.config import Settings


def test_settings_load_without_ai_credentials(monkeypatch) -> None:
    """The app must start even when no AI provider credentials are set."""
    for var in (
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "FIGMA_ACCESS_TOKEN",
        "QDRANT_URL",
        "QDRANT_API_KEY",
    ):
        monkeypatch.delenv(var, raising=False)

    settings = Settings(_env_file=None)

    assert settings.openai_api_key is None
    assert settings.anthropic_api_key is None
    assert settings.figma_access_token is None
    assert settings.qdrant_url is None
    assert settings.qdrant_collection == "mui_component_docs"


def test_cors_origins_list_splits_and_trims() -> None:
    settings = Settings(_env_file=None, cors_origins="http://localhost:3000, http://127.0.0.1:3000")

    assert settings.cors_origins_list == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
