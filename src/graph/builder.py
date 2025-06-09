from langgraph.graph import StateGraph, START

from .types import State
from .nodes import (
    supervisor_node,
    research_node,
    code_node,
    coordinator_node,

    reporter_node,
    planner_node,
    db_analyst_node,
    document_parser_node,
    chart_generator_node,
)


def build_graph():
    """Build and return the agent workflow graph."""
    builder = StateGraph(State)
    builder.add_edge(START, "coordinator")
    builder.add_node("coordinator", coordinator_node)
    builder.add_node("planner", planner_node)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("researcher", research_node)
    builder.add_node("coder", code_node)

    builder.add_node("reporter", reporter_node)
    builder.add_node("db_analyst", db_analyst_node)
    builder.add_node("document_parser", document_parser_node)
    builder.add_node("chart_generator", chart_generator_node)
    return builder.compile()
