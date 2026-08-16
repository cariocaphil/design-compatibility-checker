"""Centralized application configuration.

All backend configuration should be read through :class:`Settings` rather than
accessed via ``os.environ`` directly elsewhere in the codebase. This keeps
environment/configuration concerns in one place per PROJECT_SPEC.md section 24.

AI-provider and retrieval settings are intentionally optional at this stage:
Phase 1 PR 1 only establishes the application foundation (no AI pipeline
functionality yet), so the application must start successfully even when
provider credentials are absent. Later PRs that consume these values are
responsible for handling the "not configured" case explicitly.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Backend application settings, sourced from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- General ---
    app_name: str = "Design Compatibility Checker API"
    environment: str = "development"

    # --- CORS ---
    # Comma-separated list of allowed browser origins.
    cors_origins: str = "http://localhost:3000"

    # --- OpenAI (used by later PRs for vision/semantic analysis) ---
    openai_api_key: str | None = None
    openai_vision_model: str | None = None
    openai_semantic_model: str | None = None

    # --- Anthropic (used by a later PR for compatibility matching) ---
    anthropic_api_key: str | None = None
    anthropic_matcher_model: str | None = None

    # --- Figma (used by a later PR for the Figma input path) ---
    figma_access_token: str | None = None

    # --- Qdrant (used by a later PR for Material UI retrieval) ---
    qdrant_url: str | None = None
    qdrant_api_key: str | None = None
    qdrant_collection: str = "mui_component_docs"

    @property
    def cors_origins_list(self) -> list[str]:
        """Return `cors_origins` split into a list of trimmed origins."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached `Settings` instance.

    Cached so environment parsing happens once per process while still
    remaining easily overridable in tests via dependency overrides.
    """
    return Settings()
