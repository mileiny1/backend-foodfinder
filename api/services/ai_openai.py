import os 
import json 
import requests
from typing import List


OPENAI_URL = "https://api.openai.com/v1/responses"

def expand_food_query(query: str) -> List[str]:
    api_key = os.getenv("OPENAI_API_KEY")
    module = os.getenv("OPENAI_MODEL", "gpt-5.1-chat-latest")
    if not api_key:
        return _fallback_terms(query)
    system = {
        
    }
   