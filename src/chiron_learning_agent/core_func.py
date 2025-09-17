import os
from typing import List
from dotenv import load_dotenv

load_dotenv()
from chiron_learning_agent.pydantic_models import (
    LearningState,
    Checkpoints,
    SearchQuery,
    QuestionOutput,
    InContext,
    LearningCheckpoint,
)
from chiron_learning_agent.prompts import (
    checkpoint_based_query_generator,
    learning_checkpoints_generator,
    question_generator,
    validate_context,
)
from chiron_learning_agent.context_storage import ContextStorage

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from semantic_chunkers import StatisticalChunker
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utils.math import cosine_similarity

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
context_storage = ContextStorage()

tavily_search = TavilySearchResults()


# Step 1: Generate checkpoints
def generate_checkpoints(state: LearningState):
    """Creates learning checkpoints based on given topic and goals"""
    structures_llm = llm.with_structured_output(Checkpoints)
    messages = [
        SystemMessage(content=learning_checkpoints_generator),
        SystemMessage(content=f"Topic: {state['topic']}"),
        SystemMessage(content=f"Goals: {", ".join(state['goals'])}"),
    ]
    response = structures_llm.invoke(messages)
    return {"checkpoints": response}


def route_context(state: LearningState):
    """Determines whether to process existing context or generate new search queries."""

    if state.get("context"):
        return "chunk_context"
    else:
        return "generate_query"


# Step 2.1: Generate search queries
def generate_query(state: LearningState):
    """Generates search queries based on learning checkpoints from current state."""
    structured_llm = llm.with_structured_output(SearchQuery)
    checkpoints_message = HumanMessage(
        content=format_checkpoints_as_message(state["checkpoints"])
    )
    messages = [checkpoint_based_query_generator, checkpoints_message]
    search_queries = structured_llm.invoke(messages)
    return {"search_queries": search_queries}


def format_checkpoints_as_message(checkpoints: Checkpoints) -> str:
    """Convert checkpoints object to a formatted string for the message.

    Args:
        checkpoints: Checkpoints containing learning checkpoints

    Return:
        str: Formatted string containing numbered checkpoints with descriptions with descriptions and criteria
    """
    message = "Here are the learning checkpoints:\n"
    for i, checkpoint in enumerate(checkpoints.checkpoints, 1):
        message += f"Checkpoint {i}:\n"
        message += f"Description: {checkpoint.description}\n"
        message += "Success Criteria:\n"
        for criterion in checkpoint.criteria:
            message += f"- {criterion}\n"
    return message


# Step 2.2: Chunk context
def chunk_context(state: LearningState):
    """Splits context into manageable chunks and generates their embeddings"""

    encoder = embeddings_model
    chunker = StatisticalChunker(encoder, min_split_tokens=128, max_split_tokens=512)

    chunks = chunker([state["context"]])
    content = []
    for chunk in chunks:
        content.append(chunk.content)
    embeddings = encoder.embed_documents(content)
    context_key = context_storage.save_context(
        chunks, embeddings, key=state.get("context_key")
    )
    return {"context_key": context_key}


# Step 3: Web search
def search_web(state: LearningState):
    """Retrieves and processes web search results"""
    search_queries = state["search_queries"].search_queries
    all_search_docs = []
    for query in search_queries:
        search_docs = tavily_search.invoke(query)
        all_search_docs.extend(search_docs)

    formatted_search_docs = []
    for doc in all_search_docs:
        formatted_search_docs.append(
            f"Context: {doc.get('context', 'N/A')}\n Source: {doc.get('url', 'N/A')}\n"
        )
    chunk_embeddings = embeddings_model.embed_documents(formatted_search_docs)
    context_key = context_storage.save_context(
        formatted_search_docs, chunk_embeddings, key=state.get("context_key")
    )
    return {"context_chunks": formatted_search_docs}


# Step 4: Generate questions
def generate_questions(state: LearningState):
    """Generates assessment questions based on current checkpoint verification requirements."""
    structured_llm = llm.with_structured_output(QuestionOutput)
    current_checkpoint = state["current_checkpoint"]
    checkpoint_info = state["checkpoints"].checkpoints[current_checkpoint]
    messages = [
        SystemMessage(content=question_generator),
        HumanMessage(
            content=f"""
            Checkpoint Description: {checkpoint_info.description}
            Success Criteria: {checkpoint_info.criteria}
            Verification Method: {checkpoint_info.verification}
            
            Generate an appropriate verification question.
            """
        ),
    ]
    question = structured_llm.invoke(messages)
    return {"current_question": question.question}


# Step 2.2.2: Verify checkpoint
def context_validation(state: LearningState):
    """Validate context coverage against checkpoint criteria using stored embeddings"""
    context = context_storage.get_context(state["context_key"])
    chunks = context["chunks"]
    chunk_embeddings = context["embeddings"]

    checks = []
    structured_llm = llm.with_structured_output(InContext)

    for checkpoint in state["checkpoints"].checkpoints:
        query = embeddings_model.embed_query(checkpoint.verification)
        similarity = cosine_similarity([query], chunk_embeddings)[0]
        top_3_indices = sorted(
            range(len(similarity)), key=lambda i: similarity[i], reverse=True
        )[:3]
        relevant_chunks = [chunks[i] for i in top_3_indices]

        messages = [
            SystemMessage(content=validate_context),
            HumanMessage(
                context=f"""
                Criteria:
                {chr(10).join(f"- {c}" for c in checkpoint.criteria)}
                
                Context:
                {chr(10).join(relevant_chunks)}
                """
            ),
        ]
        
        response = structured_llm.invoke(messages)
        if response.is_in_context.lower() == "no":
            checks.append(checkpoint)
            
        
    if checks:
        structured_llm = llm.with_structured_output(SearchQuery)
        checkpoints_message = generate_checkpoint_message(checks)
        
        messages = [checkpoint_based_query_generator, checkpoints_message]
        search_queries = structured_llm.invoke(messages)
        return {"search_queries": search_queries}
    
    return {"search_queries": None}



def generate_checkpoint_message(checks: List[LearningCheckpoint]) -> HumanMessage:
    """Generate a formatted message for learning checkpoints that need context.
    
    Args:
        checks (List[LearningCheckpoint]): List of learning checkpoint objects
        
    Returns:
        HumanMessage: Formatted message containing checkpoint descriptions, criteria and 
                     verification methods, ready for context search
    """
    formatted_checks = []
    
    for check in checks:
        checkpoint_text = f"""
        Description: {check.description}
        Success Criteria:
        {chr(10).join(f'- {criterion}' for criterion in check.criteria)}
        Verification Method: {check.verification}
        """
        formatted_checks.append(checkpoint_text)
    
    all_checks = "\n---\n".join(formatted_checks)
    
    checkpoints_message = HumanMessage(content=f"""The following learning checkpoints need additional context:
        {all_checks}
        
        Please generate search queries to find relevant information.""")
    
    return checkpoints_message
