from typing import Annotated, Optional, Sequence, TypedDict, Dict
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class SearchPapersInput(BaseModel):
    query: str = Field(description="The query to search for on the selected archive.")
    max_papers: int = Field(description="The maximum number of papers to return. It's default to 1, but you can increase it up to 10 in case you need to perform a more comprehensive search.", default=1, ge=1, le=10)
    
class DecisionMakingOutput(BaseModel):
    requires_research: bool = Field(description="Whether the user query requires research or not.")
    answer: Optional[str] = Field(default=None, description="The answer to the user query. It should be None if the user query requires research, otherwise it should be a direct answer to the user query.")
    
class JudgeOutput(BaseModel):
    is_good_answer: bool = Field(description="Whether the answer is good or not.")
    feedback: Optional[str] = Field(default=None, description="Detailed feedback about why the answer is not good. It should be None if the answer is good.")

class AgentState(TypedDict):
    """The state of the agent during the paper research process"""
    requires_research: bool = False
    num_papers_searched: int = 0
    is_good_answer: bool = False
    num_planning_cycles: int = 0  # Track planning-agent-judge cycles
    messages: Annotated[Sequence[BaseMessage], add_messages]
    