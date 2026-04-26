"""TEContext — dependency injection interface for TE packages.

The AE provides a TEContext to each TE's build_graph() function.
The TE uses it to access tools, checkpointer, config, inference,
database, logging, and metrics without importing from app.* directly.

This is the contract between AE and TE packages (ERQ-002 §12.3, §13.2).
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class TEContext(Protocol):
    """Interface that the AE provides to TE packages.

    TE packages receive this in build_graph(context) and use it
    instead of importing from app.tools, app.config, app.checkpointer.

    Covers ERQ-002 §13.2 base contract surface:
    - Tools (get_tools_for_model, get_all_tools)
    - Checkpointer (get_checkpointer)
    - Inference (get_api_key, get_chat_model)
    - Configuration (load_config)
    - Database (get_db_pool)
    - Logging (get_logger)
    - Metrics (get_metrics_registry)
    """

    # ── Tools ────────────────────────────────────────────────────

    def get_tools_for_model(self, model_name: str, tool_names: list[str]) -> list:
        """Return tool callables for the given model, filtered by config."""
        ...

    def get_all_tools(self) -> dict[str, Any]:
        """Return the full tool registry dict."""
        ...

    # ── Checkpointer ─────────────────────────────────────────────

    def get_checkpointer(self) -> Any:
        """Return the AsyncPostgresSaver checkpointer for conversation state."""
        ...

    # ── Inference ────────────────────────────────────────────────

    def get_api_key(self, llm_config: dict) -> str | None:
        """Resolve an API key from the llm_config's api_key_env field."""
        ...

    def get_chat_model(self, llm_config: dict) -> Any:
        """Return a configured ChatOpenAI instance from llm_config."""
        ...

    # ── Configuration ────────────────────────────────────────────

    def load_config(self) -> dict:
        """Load the merged config (config.yml + te.yml)."""
        ...

    # ── Database ─────────────────────────────────────────────────

    def get_db_pool(self) -> Any:
        """Return the asyncpg connection pool for database access."""
        ...

    # ── Logging ──────────────────────────────────────────────────

    def get_logger(self, name: str) -> Any:
        """Return a configured logger for the given name."""
        ...

    # ── Metrics ──────────────────────────────────────────────────

    def get_metrics_registry(self) -> Any:
        """Return the Prometheus CollectorRegistry for metrics registration."""
        ...

    # ── Peer Proxy ───────────────────────────────────────────────

    def get_peer_proxy(self) -> Any:
        """Return a client for reaching other MADs in the ecosystem (ERQ-002 §13.2)."""
        ...
