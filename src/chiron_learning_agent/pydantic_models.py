from typing import Annotated, List, Dict, Any, TypedDict
from pydantic import BaseModel, Field

class LearningState(TypedDict):
    topic: str = Field(description="The topic of the learning")
    goals: List[str] = Field(description="The goals of the learning")
    
class LearningCheckpoints(BaseModel):
    """Structure for single checkpoint"""
    description: str = Field(description="Level check point description")
    criteria: List[str] = Field(description="Criteria to verify the checkpoint")
    verification: str = Field(description="How to verify this checkpoint(Feynmen Methods)")
    
class Checkpoints(BaseModel):
    """Structure for all checkpoints"""
    checkpoints: List[LearningCheckpoints] = Field(description="List of checkpoints")
    
class SearchQuery(BaseModel):
    """Structure for search query collection"""
    search_queries: List[str] = Field(None, description="Search queries for retrieval.")
    

    
    
    