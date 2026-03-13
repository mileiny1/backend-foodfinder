from typing import List, Dict, Optional # for type annotations
from django.conf import settings # for accessing Django settings, which may include API keys and other configuration
from .places_yelp import search_yelp # import the search_yelp function from the places_yelp module
from .places_google import search_google # import the search_google function from the places_google module

def search_places( # main function to search for places using both Google and Yelp APIs
        provider: Optional[str], # optional parameter to specify which provider to use (Google, Yelp, or both)
        lat: float, # latitude for the search location
        lng: float, # longitude for the search location
        turn: str, # a string parameter that may be used for logging or other purposes to indicate the context of the search
        radius_m: int, # search radius in meters
        open_now: Optional[bool],# optional parameter to filter results to only those that are currently open
        price_range: Optional[str], # optional parameter to filter results by price range (e.g., "1,2" for cheap and moderate)
        limit: int,    # limit on the number of results to return from each provider
) -> List[Dict]:
    p = (provider or settings.PLACES_PROVIDER or "yelp").lower().strip() # determine which provider to use based on the input parameter, settings, or default to "yelp"
    if p == "yelp":
        return search_yelp(lat, lng, term= term, radius_m = radius_m, open_now = open_now,price_range = price_range, limit = limit) # if the provider is Yelp, call the search_yelp function with the appropriate parameters and return the results.
    if p == "google":
        return search_google(lat, lng, keywords = term, radius_m = radius_m, open_now = open_now, limit = limit) # if the provider is Google, call the search_google function with the appropriate parameters and return the results.
    
    raise ValueError("invalid provider. use 'yelp', 'google'.") # if the provider parameter is not valid, raise a ValueError with a message indicating the valid options for the provider.
