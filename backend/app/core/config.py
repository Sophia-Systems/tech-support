"""Two-layer config: env vars (secrets/infra) + YAML overlay (behavior/tuning)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"


def _load_yaml(path: Path) -> dict[str, Any]:
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f) or {}
    return {}


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_", env_file=_ENV_FILE, extra="ignore")

    host: str = "localhost"
    port: int = 5432
    db: str = "customer_service_bot"
    user: str = "csbot"
    password: str = "changeme"

    @property
    def async_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    @property
    def sync_url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_", env_file=_ENV_FILE, extra="ignore")

    url: str = "redis://localhost:6379/0"


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LLM_", env_file=_ENV_FILE, extra="ignore")

    model: str = "gpt-4o-mini"
    api_key: str = ""
    api_base: str | None = None
    temperature: float = 0.1
    max_tokens: int = 1024


class EmbeddingSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="EMBEDDING_", env_file=_ENV_FILE, extra="ignore")

    provider: str = "litellm"
    model: str = "text-embedding-3-small"
    api_key: str = ""
    dimension: int = 1536


class RerankerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RERANKER_", env_file=_ENV_FILE, extra="ignore")

    provider: str = "cross-encoder"
    model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    api_key: str = ""


class VectorStoreSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="VECTORSTORE_", env_file=_ENV_FILE, extra="ignore")

    provider: str = "pgvector"


class LangFuseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LANGFUSE_", env_file=_ENV_FILE, extra="ignore")

    public_key: str = ""
    secret_key: str = ""
    host: str = "http://localhost:3100"
    enabled: bool = True


class EscalationSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ESCALATION_", env_file=_ENV_FILE, extra="ignore")

    webhook_url: str = ""


class IngestionSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="INGESTION_", env_file=_ENV_FILE, extra="ignore")

    allowed_base_dir: str = ""
    max_upload_size_mb: int = 50


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=_ENV_FILE, extra="ignore")

    env: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    cors_origins: list[str] = Field(default=["http://localhost:5173"])
    api_key: str = ""


class RetrievalConfig:
    """Loaded from YAML — retrieval pipeline tuning parameters."""

    def __init__(self, data: dict[str, Any] | None = None):
        d = data or {}
        self.semantic_top_k: int = d.get("semantic_top_k", 20)
        self.keyword_top_k: int = d.get("keyword_top_k", 20)
        self.rrf_k: int = d.get("rrf_k", 60)
        self.rerank_top_k: int = d.get("rerank_top_k", 5)
        self.chunk_size: int = d.get("chunk_size", 512)
        self.chunk_overlap: int = d.get("chunk_overlap", 64)


class ConfidenceConfig:
    """Loaded from YAML — confidence tier thresholds."""

    def __init__(self, data: dict[str, Any] | None = None):
        d = data or {}
        self.answer_threshold: float = d.get("answer_threshold", 0.85)
        self.caveat_threshold: float = d.get("caveat_threshold", 0.60)
        self.decline_threshold: float = d.get("decline_threshold", 0.35)
        self.minimum_relevance: float = d.get("minimum_relevance", 0.15)
        self.ambiguity_score_variance: float = d.get("ambiguity_score_variance", 0.05)


class PersonaConfig:
    """Loaded from YAML — persona template + variables."""

    def __init__(self, data: dict[str, Any] | None = None):
        d = data or {}
        self.company_name: str = d.get("company_name", "our company")
        self.product_name: str = d.get("product_name", "our product")
        self.tone: str = d.get("tone", "professional and helpful")
        self.template_path: str = d.get("template_path", "persona/default.yaml")


class Settings:
    """Aggregated settings from env vars + YAML files."""

    def __init__(self) -> None:
        self.app = AppSettings()
        self.postgres = PostgresSettings()
        self.redis = RedisSettings()
        self.llm = LLMSettings()
        self.embedding = EmbeddingSettings()
        self.reranker = RerankerSettings()
        self.vectorstore = VectorStoreSettings()
        self.langfuse = LangFuseSettings()
        self.escalation = EscalationSettings()
        self.ingestion = IngestionSettings()

        yaml_data = _load_yaml(_CONFIG_DIR / "default.yaml")
        self.retrieval = RetrievalConfig(yaml_data.get("retrieval"))
        self.confidence = ConfidenceConfig(yaml_data.get("confidence"))
        self.persona = PersonaConfig(yaml_data.get("persona"))

    def reload_yaml(self) -> None:
        yaml_data = _load_yaml(_CONFIG_DIR / "default.yaml")
        self.retrieval = RetrievalConfig(yaml_data.get("retrieval"))
        self.confidence = ConfidenceConfig(yaml_data.get("confidence"))
        self.persona = PersonaConfig(yaml_data.get("persona"))


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
