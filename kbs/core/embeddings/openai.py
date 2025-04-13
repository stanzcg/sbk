import os
from typing import List, Union
import logging

from openai import OpenAI
from kbs.core.embeddings.base import BaseEmbedding

logger = logging.getLogger(__name__)

class OpenAIEmbedding(BaseEmbedding):
    """基于 OpenAI API 的 Embedding 实现"""
    
    def __init__(self, api_key: str = None, base_url: str = None, model_name: str = "text-embedding-3-small", dim: int = 1024):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url
        self.dim = dim
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
            
        self.model = model_name
        logger.debug("OpenAIEmbedding initialized with model: %s", self.model)
        
    def embed_query(self, text: str) -> List[float]:
        logger.debug("Embedding query: %s", text)
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        logger.debug("Query embedded successfully.")
        return response.data[0].embedding
        
    def embed_documents(self, texts: Union[str, List[str]]) -> List[List[float]]:
        logger.debug("Embedding documents: %s", texts)
        if isinstance(texts, str):
            texts = [texts]
        embeddings = []
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url or os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
            )
            response = self.client.embeddings.create(
                model=self.model,
                input=texts,
                dimensions=self.dim
            )
            logger.debug("Documents embedded successfully.")
            return [data.embedding for data in response.data] 
        except Exception as e:
            import requests
            for text in texts:
                payload = {
                    "model": self.model,
                    "input": text,
                    "encoding_format": "float"
                }
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                response = requests.request("POST", self.base_url, json=payload, headers=headers)
                # logger.debug(f"response: {response.text}")
                embeddings.append(response.json()["data"][0]["embedding"])
        return embeddings