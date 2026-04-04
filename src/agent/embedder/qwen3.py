import asyncio
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import torch
from torch import Tensor
from transformers import AutoModel, AutoTokenizer

from .base import Embedder


# https://huggingface.co/Qwen/Qwen3-Embedding-0.6B


def last_token_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
    left_padding = attention_mask[:, -1].sum() == attention_mask.shape[0]
    if left_padding:
        return last_hidden_states[:, -1]
    else:
        sequence_lengths = attention_mask.sum(dim=1) - 1
        batch_size = last_hidden_states.shape[0]
        return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]


def get_detailed_instruct(task_description: str, query: str) -> str:
    return f"Instruct: {task_description}\nQuery:{query}"


DEFAULT_TASK = "Given a web search query, retrieve relevant passages that answer the query"


class Qwen3Embedder(Embedder):
    """Qwen3 Embedding 0.6B."""

    def __init__(self, executor: ThreadPoolExecutor, task: str | None = None) -> None:
        self.executor = executor
        self.task = task or DEFAULT_TASK
        # TODO should use GPU device, if any
        self.tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-Embedding-0.6B", padding_side="left")
        self.model = AutoModel.from_pretrained("Qwen/Qwen3-Embedding-0.6B")
        self.size = int(self.model.embed_tokens.embedding_dim)

    async def embed_query(self, query: str) -> np.ndarray:
        document = get_detailed_instruct(self.task, query)
        return await self.embed_document(document)

    async def embed_document(self, content: str) -> np.ndarray:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, self._embed, content)

    def _embed(self, content: str) -> np.ndarray:
        # TODO should probably use batched inference
        with torch.no_grad():
            input = self.tokenizer(content, return_tensors="pt")
            output = self.model(**input)
            embeddings = last_token_pool(output.last_hidden_state, input["attention_mask"])
            embeddings = embeddings[0].to(torch.float32)
            embeddings = embeddings.numpy(force=True)
            return embeddings
