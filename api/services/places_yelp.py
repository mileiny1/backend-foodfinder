import os
import requests from typing import List, Dict,Optional
YELP_SEARCH_URL = "https://api.yelp.com/v3/businesses/search"
def search_yelp(
        lat: float,
        lng: float,
        term: str,
        radius_m: int,
        open_now: Optional[bool] = None,
        price_range: Optional[str] = None,
        limit: int,     
) -> List[Dict]:
    api_key = os.getenv("YELP_API_KEY in .env")

    params = {
        "latitude": lat,
        "longitude": lng,
        "term": term,
        "radius": min(radius_m, 40000),
        "categories": "restaurants",
        "limit": min(limit, 50),
        "sort_by": "distance",  
    }
    if open_now is True:
        params["open_now"] = "true"
        if price_range:
            params["price"] = price_range
            r = requests.get(
                YELP_SEARCH_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                params=params,
                timeout=20,
            )
            r.raise_for_status()
            data = r.json()
            results = []
            for b in data.get("businesses", []):
                results.append(
                    {
                        "name": b.get("name"),
                        "address": ",".join((b.get("location")or {})).get("display_address", []),
                        "lat": coords.get("latitude"),
                        "lng": coords.get("longitude"),
                        "rating": b.get("rating"),
                        "price_level":_price_to_level(b.get("price")),
                        "is_open_now": None,
                        "provider_place_id": b.get("id") or "",
                        "provider": "yelp",
                    }
                )
            return results
def _price_to_level(price_str):
    if not price_str:
        return None
    return len(price_str)        
               
            