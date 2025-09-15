from langgraph.graph.state import CompiledStateGraph
from typing import Optional
from langchain_core.messages import BaseMessage
from IPython.display import display, Markdown

async def print_stream(app: CompiledStateGraph, input: str)-> Optional[BaseMessage]:
    """
    Print the stream of the research process
    """
    display(Markdown("## New research running"))
    display(Markdown(f"### User query: {input}"))
    display(Markdown("### Stream:\n\n"))
    
    # Stream the results
    all_messages = []
    async for chunk in app.astream({"messages": [input]}, stream_mode="updates"):
        for updates in chunk.values():
            if messages:=updates.get("messages"): # := is a walrus operator
                all_messages.extend(messages)
                for message in messages:
                    message.pretty_print()
                    print("\n\n")
                    
    # Return the last message if any
    if not all_messages:
        return None
    return all_messages[-1]