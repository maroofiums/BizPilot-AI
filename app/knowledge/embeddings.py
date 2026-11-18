
from functools import lru_cache

from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings

from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _load_model() -> SentenceTransformer:
    """Load and cache the local embedding model."""

    try:
        logger.info(
            "Loading embedding model: %s",
            settings.embedding_model,
        )

        model = SentenceTransformer(
            settings.embedding_model,
            device="cpu",
        )

        logger.info("Embedding model loaded successfully.")

        return model

    except Exception as exc:
        logger.exception("Failed to load embedding model.")

        raise RuntimeError(
            "Unable to load the embedding model."
        ) from exc


class LocalEmbeddings(Embeddings):
    """Generate local text embeddings using Sentence Transformers."""

    @property
    def model(self) -> SentenceTransformer:
        """Return the cached embedding model."""

        return _load_model()

    @staticmethod
    def _validate_text(text: str) -> None:
        """Validate an individual text input."""

        if not isinstance(text, str) or not text.strip():
            raise ValueError(
                "Embedding input must be a non-empty string."
            )

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Generate embeddings for multiple documents."""

        if not texts:
            return []

        for text in texts:
            self._validate_text(text)

        try:
            vectors = self.model.encode(
                texts,
                batch_size=32,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )

            return vectors.tolist()

        except Exception as exc:
            logger.exception(
                "Failed to generate document embeddings."
            )

            raise RuntimeError(
                "Document embedding generation failed."
            ) from exc

    def embed_query(self, text: str) -> list[float]:
        """Generate an embedding for a single query."""

        self._validate_text(text)

        return self.embed_documents([text])[0]
