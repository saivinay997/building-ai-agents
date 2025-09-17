import time
import os
import json
from dotenv import load_dotenv
import requests
import urllib3

CORE_API_KEY = os.getenv("CORE_API_KEY")



class CoreAPIWrapper:
    
    def __init__(self, top_k_results: int = 10):
        self.base_url = "https://api.core.ac.uk/v3"
        self.api_key = CORE_API_KEY
        self.http = urllib3.PoolManager()
        self.top_k_results = top_k_results
    def _make_request(self,  query: str) -> dict:
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = self.http.request(
                'GET',
                f"{self.base_url}/search/outputs", 
                headers={"Authorization": f"Bearer {self.api_key}"}, 
                fields={"q": query, "limit": self.top_k_results}
            )
                return response.json()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(2**(attempt+2))
        
        return response.json()
    
    def search(self, query: str) -> str:
        """Search for papers on Core
        
        Args:
            query: The query to search for on the selected archive.
        
        Returns:
            A string containing the search results.
             - ID: The ID of the paper.
             - Title: The title of the paper.
             - Published Date: The published date of the paper.
             - Authors: The authors of the paper.
             - Abstract: The abstract of the paper.
             - Paper URLs: The URLs of the paper.
        """
        response = self._make_request(query)
        results = response.get("results", [])
        if not results:
            return "No relevant results were found"
        docs = []
        for result in results:
            published_data_str = result.get("publishedDate") or result.get("yearPublished", "")
            authors_str = " and ".join([item["name"] for item in result.get("authors", [])])
            docs.append((
                f"* ID: {result.get('id', '')},\n"
                f"* Title: {result.get('title', '')},\n"
                f"* Published Date: {published_data_str},\n"
                f"* Authors: {authors_str},\n"
                f"* Abstract: {result.get('abstract', '')},\n"
                f"* Paper URLs: {result.get('sourceFulltextUrls') or result.get('downloadUrl', '')}"
            ))
        return "\n-----\n".join(docs)


