from langgraph.store.memory import InMemoryStore
import uuid
class ContextStorage:
    """Store for managing context chunks and their embeddings in memory
    """
    
    def __init__(self):
        """Initialize ContextStore with an empty in-memory store"""
        self.store = InMemoryStore()
        
    def save_context(self, context_chunks: list, embeddings: list, key: str = None):
        """Save context chunks and their embeddings to the store"""
        namespace = ("context")
        if key is None:
            key = str(uuid.uuid4())    
        
        value = {
            "chunks": context_chunks,
            "embeddings": embeddings,
        }    
        self.store.put(namespace, key, value)
        return key
    
    def get_context(self, context_key: str):
        """Retrieve context data from the store using a key"""
        namespace = ("context")
        memory = self.store.get(namespace, context_key)
        return memory.value