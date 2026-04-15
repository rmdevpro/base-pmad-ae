"""TEContext — dependency injection interface for TE packages.

The AE provides a TEContext to each TE's build_graph() function.
The TE uses it to access tools, checkpointer, config, and inference
without importing from app.* directly.

This is the contract between AE and TE packages (ERQ-002 §12.3).
"""

from typing import Any, Callable, Protocol


class TEContext(Protocol):
    """Interface that the AE provides to TE packages.

    TE packages receive this in build_graph(context) and use it
    instead of importing from app.tools, app.config, app.checkpointer.
    """

    def get_tools_for_model(self, model_name: str, tool_names: list[str]) -> list:
        """Return tool callables for the given model, filtered by config."""
        ...

    def get_all_tools(self) -> dict[str, Any]:
        """Return the full tool registry dict."""
        ...

    def get_checkpointer(self) -> Any:
        """Return the AsyncPostgresSaver checkpointer."""
        ...

    def get_api_key(self, llm_config: dict) -> str | None:
        """Resolve an API key from the llm_config's api_key_env field."""
        ...

    def get_chat_model(self, llm_config: dict) -> Any:
        """Return a configured ChatOpenAI instance from llm_config."""
        ...

    def load_config(self) -> dict:
        """Load the merged config (config.yml + te.yml)."""
        ...
