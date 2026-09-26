import numpy as np
from sentence_transformers import SentenceTransformer

from utils.logger import get_logger

logger = get_logger(__name__)

MODEL_NAME = 'all-MiniLM-L6-v2'

model : SentenceTransformer | None = None

def get_model() -> SentenceTransformer:
    global model
    if model is None:
        logger.info(f"Loading sentence embedding model : {MODEL_NAME}")
        model = SentenceTransformer(MODEL_NAME)
    return model

def compute_embedding(text : str) -> bytes:
    '''
    Converts a text description into an embedding vector
    -serialized as bytes for db storage
    -returns empty bytes for empty text
    '''

    if not text:
        return b""

    model = get_model()
    vector = model.encode(text)
    
    return vector.astype(np.float32).tobytes() #float32 storage saving

def cosine_similarity(embedding1 : bytes, embedding2 : bytes) -> float:
    '''
    Compares two stored embeddings and returns their cosine similarity [-1,1] interval
    -returns 0 if no embedding to prevent crash
    '''

    if not embedding1 or not embedding2:
        return 0.0

    vec1 = np.frombuffer(embedding1, dtype=np.float32)
    vec2 = np.frombuffer(embedding2, dtype=np.float32)

    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return float(np.dot(vec1, vec2)/norm1*norm2)


