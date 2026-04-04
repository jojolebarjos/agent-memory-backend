from abc import ABC, abstractmethod

import numpy as np


class Embedder(ABC):
    """..."""

    size: int

    @abstractmethod
    async def embed_query(self, query: str) -> np.ndarray:
        pass

    @abstractmethod
    async def embed_document(self, content: str) -> np.ndarray:
        pass
