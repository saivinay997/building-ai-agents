import os
from dotenv import load_dotenv
load_dotenv()
from chiron_learning_agent.pydantic_models import LearningState, Checkpoints, SearchQuery
from chiron_learning_agent.prompts import checkpoint_based_query_generator, learning_checkpoints_generator
from chiron_learning_agent.context_storage import ContextStorage

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from semantic_chunker import StatisticalChunker
from langchain_community.tools.tavily_search import TavilySearchResults

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
    messages = [SystemMessage(content=learning_checkpoints_generator),
                SystemMessage(content=f"Topic: {state['topic']}"),
                SystemMessage(content=f"Goals: {", ".join(state['goals'])}")]
    response = structures_llm.invoke(messages)
    return {"checkpoints": response}

# Step 2.1: Generate search queries
def generate_query(state: LearningState):
    """Generates search queries based on learning checkpoints from current state."""
    structured_llm = llm.with_structured_output(SearchQuery)
    checkpoints_message = HumanMessage(content=format_checkpoints_as_message(state["checkpoints"]))
    messages = [checkpoint_based_query_generator, checkpoints_message]
    search_queries = structured_llm.invoke(messages)
    return {"search_queries": search_queries}
    
    
def format_checkpoints_as_message(checkpoints: Checkpoints) -> str:
    """ Convert checkpoints object to a formatted string for the message.
    
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
    content= []
    for chunk in chunks:
        content.append(chunk.content)
    embeddings = encoder.embed_documents(content)
    context_key = context_storage.save_context(chunks, embeddings, key= state.get("context_key"))
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