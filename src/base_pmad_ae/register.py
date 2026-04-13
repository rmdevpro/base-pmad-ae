"""
AE — Package registration entry point.

Called by the bootstrap kernel's package_registry when this package
is loaded via convention-based import.

Returns an AERegistration dict with flow builders and tool registry.
"""


def register() -> dict:
    """Register the AE's infrastructure StateGraphs and tools.

    Returns a dict with:
    - build_types: dict of (assembly_builder, retrieval_builder) pairs
    - flows: dict of flow_name -> builder callable
    - tools: the TOOL_REGISTRY dict mapping tool names to callables
    - admin_tools: set of tool names restricted to host Imperator
    - get_tools_for_model: function to get filtered tools for a model
    """
    from base_pmad_ae.health_flow import build_health_check_flow
    from base_pmad_ae.metrics_flow import build_metrics_flow
    from base_pmad_ae.autoprompt_dispatcher import build_autoprompt_dispatcher_flow
    from base_pmad_ae.embedding_worker import build_embedding_worker_flow
    from base_pmad_ae.tools import TOOL_REGISTRY, ADMIN_TOOLS, get_tools_for_model

    return {
        "build_types": {},
        "flows": {
            "health_check": build_health_check_flow,
            "metrics": build_metrics_flow,
            "autoprompt_dispatcher": build_autoprompt_dispatcher_flow,
            "embedding_worker": build_embedding_worker_flow,
        },
        "tools": TOOL_REGISTRY,
        "admin_tools": ADMIN_TOOLS,
        "get_tools_for_model": get_tools_for_model,
    }
