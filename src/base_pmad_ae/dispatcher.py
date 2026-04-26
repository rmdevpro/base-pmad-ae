"""AE Graph Dispatcher — owns all routing logic for chat requests.

ERQ-002 §2: No application logic in route handlers. Route handlers invoke
StateGraphs. This class owns: model lookup, package loading, graph caching.

WHY THIS IS A PYTHON CLASS AND NOT A LANGGRAPH STATEGRAPH:
The ideal architecture would have the dispatch layer be a LangGraph StateGraph
(consistent with the rest of the system). However, LangGraph does not propagate
astream_events() through dynamic ainvoke() calls between separately compiled
graphs. If the dispatch graph called te_graph.ainvoke() from within a node,
on_chat_model_stream events from the TE's LLM calls would not be captured by
the outer graph's event stream — streaming would be silently broken.

The only LangGraph workaround is compile-time subgraph wiring
(builder.add_node("te", compiled_te_graph)), which requires knowing the TE at
build time. We have dynamic routing (model name → TE graph at runtime), so
compile-time wiring is not possible.

The practical solution: GraphDispatcher is a Python class that owns all routing
logic, satisfying ERQ-002 §2 (AE owns routing, not the route handler). The HTTP
receiver calls get_graph(model_name) and streams directly from the returned TE
graph. Streaming works because there is no intermediary graph in the call path.

If LangGraph adds support for dynamic subgraph streaming in a future version,
this class should be converted to a StateGraph.
"""

import logging
from typing import Any

_log = logging.getLogger("base_pmad_ae.dispatcher")

_graph_cache: dict = {}


def invalidate_cache() -> None:
    """Clear the graph cache. Called after package install/hot-reload."""
    _graph_cache.clear()
    _log.info("Graph cache invalidated")


class GraphDispatcher:
    """Routes model names to compiled TE graphs.

    Owns: DB lookup, package loading, graph caching.
    Route handlers call get_graph() and stream directly from the result.
    """

    def __init__(self, context: Any) -> None:
        self._context = context

    async def get_graph(self, model_name: str):
        """Return the compiled TE graph for the given model name, or None."""
        if model_name in _graph_cache:
            return _graph_cache[model_name]

        graph = await self._load_graph(model_name)
        if graph is not None:
            _graph_cache[model_name] = graph
        return graph

    async def _load_graph(self, model_name: str):
        if model_name == "host":
            return self._load_host_graph()

        pool = self._context.get_db_pool()
        try:
            row = await pool.fetchrow(
                "SELECT package_name FROM emad_instances"
                " WHERE emad_name = $1 AND status = 'active'",
                model_name,
            )
        except (RuntimeError, OSError) as exc:
            _log.warning("DB lookup failed for model '%s': %s", model_name, exc)
            return None

        if row is None:
            return None

        package_name = row["package_name"]
        return self._load_emad_graph(model_name, package_name)

    def _load_host_graph(self):
        from app.package_registry import get_imperator_builder
        builder = get_imperator_builder()
        if builder is None:
            _log.warning("No Imperator builder registered")
            return None
        return builder()

    def _load_emad_graph(self, model_name: str, package_name: str):
        from app.package_registry import get_build_func, load_emad
        build_func = get_build_func(package_name)
        if build_func is None:
            try:
                load_emad(package_name)
                build_func = get_build_func(package_name)
            except (ImportError, AttributeError) as exc:
                _log.warning(
                    "Failed to load package '%s' for model '%s': %s",
                    package_name, model_name, exc,
                )
                return None
        if build_func is None:
            _log.warning("No build_graph for package '%s'", package_name)
            return None
        return build_func(self._context)
