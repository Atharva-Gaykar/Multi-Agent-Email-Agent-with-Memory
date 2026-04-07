import requests
from typing import List
from langchain_core.embeddings import Embeddings

class RemoteAPIEmbeddings(Embeddings):
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Call the /embed_docs endpoint."""
        response = requests.post(
            f"{self.base_url}/embed_docs",
            json={"texts": texts}
        )
        response.raise_for_status()
        return response.json()["embeddings"]

    def embed_query(self, text: str) -> List[float]:
        """Call the /embed_query endpoint."""
        response = requests.post(
            f"{self.base_url}/embed_query",
            json={"text": text}
        )
        response.raise_for_status()
        return response.json()["embedding"]
    

API_BASE_URL = "https://gaykar-generalembeddings.hf.space"

remote_embeddings = RemoteAPIEmbeddings(base_url=API_BASE_URL)