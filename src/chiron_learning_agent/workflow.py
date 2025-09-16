from langgraph.graph import StateGraph, START, END

from chiron_learning_agent.core_func import generate_checkpoints, generate_query
from chiron_learning_agent.pydantic_models import LearningState


agent_graph = StateGraph(LearningState)

agent_graph.add_node("generate_checkpoints", generate_checkpoints)
agent_graph.add_node("generate_query", generate_query)