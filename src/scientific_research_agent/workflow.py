import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END

from scientific_research_agent.prompts import (
    decision_making_prompt,
    judge_prompt,
    planning_prompt,
    agent_prompt,
)
from scientific_research_agent.pydantic_models import DecisionMakingOutput, JudgeOutput
from scientific_research_agent.agent_tools import (
    tools,
    format_tool_description,
    tools_dict,
)
from scientific_research_agent.pydantic_models import AgentState


base_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
decision_making_llm = base_llm.with_structured_output(DecisionMakingOutput)
agent_llm = base_llm.bind_tools(tools)
judge_llm = base_llm.with_structured_output(JudgeOutput)


# Decision making node
def decision_making_node(state: AgentState):
    """
    Enter point of the workflow. Based on the user query, the model can either respond directly or trigger the research workflow.
    """
    #print("#" * 50)
    #print("Decision making node input:", state["messages"][-1])
    system_prompt = SystemMessage(content=decision_making_prompt)
    response: DecisionMakingOutput = decision_making_llm.invoke(
        [system_prompt] + state["messages"]
    )
    output = {"requires_research": response.requires_research}
    #print("Decision making node output:", output)
    if response.answer:
        output["answer"] = [AIMessage(content=response.answer)]
    return output


# Task router function
def router(state: AgentState):
    #print("#" * 50)
    #print("Router node input:", state)
    """Router directing the user query to the appropriate branch of the workflow"""
    if state["requires_research"]:
        return "planning"
    else:
        return "end"


# Planning Node
def planning_node(state: AgentState):
    #print("#" * 50)
    #print("Planning node input:", state["messages"][-1])
    """Planning node that creates a step by step plan to answer the user query."""
    # Increment planning cycle counter
    num_planning_cycles = state.get("num_planning_cycles", 0) + 1
    
    system_prompt = SystemMessage(
        content=planning_prompt.format(tools=format_tool_description(tools))
    )
    response = base_llm.invoke([system_prompt] + state["messages"])
    #print("Planning node output:", response)
    return {
        "messages": [response],
        "num_planning_cycles": num_planning_cycles
    }


# Tool call node
def tools_node(state: AgentState):
    """Tool call node that executes the tools based on the plan."""
    #print("#" * 50)
    #print("Tools node input:", state["messages"][-1])
    #print("Tools node - tool calls:", state["messages"][-1].tool_calls)
    outputs = []
    for tool_call in state["messages"][-1].tool_calls:
        tool_result = tools_dict[tool_call["name"]].invoke(tool_call["args"])
        outputs.append(
            ToolMessage(
                content=json.dumps(tool_result),
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )
        )
    #print("Tools node output:", outputs)
    return {"messages": outputs}


# Agent call node
def agent_node(state: AgentState):
    """Agent call node that uses the LLM with tools to answer the user query."""
    #print("#" * 50)
    #print("Agent node input:", state["messages"][-1])
    
    system_prompt = SystemMessage(content=agent_prompt)
    state["messages"][-1].content = re.sub(r"```.*?```", "", state["messages"][-1].content, flags=re.DOTALL)
    messages_to_send = [system_prompt] + state["messages"]
    
    response = agent_llm.invoke(messages_to_send)
    
    
    #print("Agent node output:", response)
    return {"messages": [response]}
    


# Should continue function
def should_continue(state: AgentState):
    """Check if the agent should continue or end."""
    #print("#" * 50)
    messages = state["messages"]
    last_message = messages[-1]
    #print("Should continue node input:", last_message)
    #print("Should continue node input:", last_message.tool_calls)
    if last_message.tool_calls:
        return "continue"
    else:
        return "end"


def judge_node(state: AgentState):
    """Node to let the LLM judge the quality of its own final answer."""
    #print("#" * 50)
    #print("Judge node input:", state["messages"][-1])
    # End execution if the LLM failed to provide a good answer twice
    num_feedback_requests = state.get("num_feedback_requests", 0)
    if num_feedback_requests >= 2:
        return {"is_good_answer": True}

    system_prompt = SystemMessage(content=judge_prompt)
    response: JudgeOutput = judge_llm.invoke([system_prompt] + state["messages"])
    output = {
        "is_good_answer": response.is_good_answer,
        "num_feedback_requests": num_feedback_requests + 1,
    }
    if response.feedback:
        output["messages"] = [AIMessage(content=response.feedback)]
        #print("Judge node output:", output["messages"][-1])
    return output


def termination_node(state: AgentState):
    """Node to handle graceful termination when max cycles are reached."""
    #print("#" * 50)
    #print("Termination node input:", state["messages"][-1])
    termination_message = AIMessage(
        content="I've reached the maximum number of attempts to provide a satisfactory answer. "
               "While I may not have fully met your expectations, I've provided the best response "
               "possible with the available information and tools. Please let me know if you'd like "
               "me to try a different approach or if you have additional questions."
    )
    #print("Termination node output:", termination_message)
    return {
        "messages": [termination_message],
        "is_good_answer": True  # Force termination
    }


# Final answer router function
def final_answer_router(state: AgentState):
    """Router to determine the final answer to the user query."""
    #print("#" * 50)
    #print("Final answer router input:", state["messages"][-1])
    if state["is_good_answer"]:
        return "end"
    else:
        # Check if we've exceeded maximum planning cycles
        num_planning_cycles = state.get("num_planning_cycles", 0)
        max_planning_cycles = 3  # Maximum number of planning-agent-judge cycles
        
        if num_planning_cycles >= max_planning_cycles:
            #print("Final answer router - terminating due to max planning cycles")
            # Route to termination node instead of returning dict
            return "termination"
        else:
            #print("Final answer router - continuing to planning")
            return "planning"


### Workflow definition

# Initialize the StateGraph
workflow = StateGraph(AgentState)

# Add nodes to the graph
workflow.add_node("decision_making", decision_making_node)
workflow.add_node("planning", planning_node)
workflow.add_node("tools", tools_node)
workflow.add_node("agent", agent_node)
workflow.add_node("judge", judge_node)
workflow.add_node("termination", termination_node)

# Set the entry point of the graph
workflow.set_entry_point("decision_making")

# Add edges between nodes
workflow.add_conditional_edges(
    "decision_making",
    router,
    {"planning": "planning", "end": END},
)
workflow.add_edge("planning", "agent")
workflow.add_edge("tools", "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {"continue": "tools", "end": "judge"},
)
workflow.add_conditional_edges(
    "judge",
    final_answer_router,
    {"end": END, "planning": "planning", "termination": "termination"},
)
workflow.add_edge("termination", END)

# compile the graph
app = workflow.compile()




