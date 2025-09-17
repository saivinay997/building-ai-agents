from langgraph.graph import StateGraph, START, END

from chiron_learning_agent.core_func import (
    generate_checkpoints,
    generate_query,
    generate_questions,
    search_web,
    route_context,
)
from chiron_learning_agent.pydantic_models import LearningState


agent_graph = StateGraph(LearningState)

agent_graph.add_node("generate_checkpoints", generate_checkpoints)
agent_graph.add_node("generate_query", generate_query)
agent_graph.add_node("search_web", search_web)
agent_graph.add_node("generate_questions", generate_questions)



#Flow
agent_graph.add_edge(START, "generate_checkpoints")
agent_graph.add_conditional_edges("generate_checkpoints", route_context, ["chunk_context", "generate_query"])
agent_graph.add_edge("generate_query", "search_web")
agent_graph.add_edge("search_web", "generate_questions")
agent_graph.add_edge("chunk_context", "context_validation")

