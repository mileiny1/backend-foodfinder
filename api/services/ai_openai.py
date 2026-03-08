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
     "You expand a user's food craving into short, keyword phrases suitable for restaurant search APIs."
     "Return ONLY JSON with this shape {\"terms\": [\"...\", ...]}. "
     "Max 6 terms. No extra keys"
        
    }
    payload = {
        "model": model,
        "input":[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Food query: {query}"}
           
        ],
        "text": {"format":{"type":"json_object"}}
    }
    r = requests.post(
        OPENAI_URL,
        headers={"Authorization": f"Bearer {api_key}",
        "Content-type": "application/json",
        },
        json=payload,
        timeout = 20,

     
   )
    r.raise_for_status
    data = r.json()

    text_parts = []
    for item in data.get("output", []):
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") == "output_text":
                    text_parts.append(c.get("text", ""))
    joined = " ".join(text_parts).strip()
    if not joined:
        return _fallback_terms(query)
    try:
        obj = json.loads(joined)
        terms = obj.get("terms", [])
        return _clean_terms(query, terms)
    except Exception:
        return _fallback_terms(query) 
def _fallback_terms(query: str) -> List[str]:
    q = query.strip()
    base = [q, f"{q} restaurant"]
    return list(dict.fromkeys([t for t in base if t]))
def _clean_terms(original: str, terms: List[str]) -> List[str]:
    cleaned = []
    for t in (terms or [])[:6]:
        t = (t or "").strip()
        if t:
            cleaned.append(t)
    if not cleaned:
        return _fallback_terms(original)
    return list(dict.fromkeys(cleaned))




    

        
    
                
      


