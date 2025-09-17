import operator
from typing import Annotated, List, Dict, Any, TypedDict
from pydantic import BaseModel, Field

class SearchQuery(BaseModel):
    """Structure for search query collection"""
    search_queries: List[str] = Field(None, description="Search queries for retrieval.")

class LearningCheckpoints(BaseModel):
    """Structure for single checkpoint"""
    description: str = Field(description="Level check point description")
    criteria: List[str] = Field(description="Criteria to verify the checkpoint")
    verification: str = Field(description="How to verify this checkpoint(Feynmen Methods)")
    
class Checkpoints(BaseModel):
    """Structure for all checkpoints"""
    checkpoints: List[LearningCheckpoints] = Field(description="List of checkpoints")
    
class QuestionOutput(BaseModel):
    """Structure for question output"""
    question: str    

class InContext(BaseModel):
    is_in_context: str = Field(..., description="Yes or NO")

# Main state
class LearningState(TypedDict):
    topic: str = Field(description="The topic of the learning")
    goals: List[str] = Field(description="The goals of the learning")
    context: str = Field(description="The context of the learning")
    context_chunks: Annotated[list, operator.add]
    context_key: str = Field(description="The key of the context")
    search_queries: SearchQuery = Field(description="The search queries for the learning")
    checkpoints: Checkpoints = Field(description="The checkpoints for the learning")
    current_question: QuestionOutput = Field(description="The current question for the learning")
    

    


    

    
    