from sentence_transformers import SentenceTransformer

from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class EmbeddingModelSingleton:
    _model = None

    @classmethod
    def get_model(cls, model_name: str = "sentence-transformers/all-mpnet-base-v2"):
        if cls._model is None:
            logger.info(f"Loading embedding model: {model_name}")
            cls._model = SentenceTransformer(model_name)
            logger.info("Embedding model loaded and ready")
        return cls._model


class EmbeddingModel:
    def __init__(self, model_name="sentence-transformers/all-mpnet-base-v2"):
        self.model = EmbeddingModelSingleton.get_model(model_name)

    def embed(self, texts):
        return self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).tolist()


# class EmbeddingModel:
#     def __init__(self, model_name="BAAI/bge-base-en-v1.5"):
#         self.model = SentenceTransformer(model_name)

#     def embed(self, texts):
#         return self.model.encode(
#             texts,
#             convert_to_numpy=True,
#             normalize_embeddings=True
#         ).tolist()
    

