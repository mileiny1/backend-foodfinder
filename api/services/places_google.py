import os # for environment variables
import requests # for making HTTP requests
from typing import List, Dict, Optional # for type annotations
GOOGLE_NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json" # Google Places API endpoint for nearby search

def search_google(
        lat: float,
        lng: float,
        keywords: str,
        radius_m: int,
        open_now: Optional[bool],
        limit: int,    
)   -> List[Dict]: # function to search for places using Google Places API
    api_key = os.getenv("GOOGLE_PLACES_API_KEY") # get the API key from environment variables
    if not api_key:
        raise RuntimeError("missing GOOGLE_PLACES_API_KEY environment in .env") # raise an error if the API key is not set
    params = {
        "key": api_key,
        "location": f"{lat},{lng}",
        "radius": radius_m,
        "keyword": keywords,
        "type": "restaurant",
    } # set up the parameters for the API request
    if open_now is True: # if the open_now parameter is True, add it to the parameters for the API request
        params["opennow"] = "true" # Google Places API uses "opennow" as the parameter name for filtering results to only those that are currently open
    r = requests.get(GOOGLE_NEARBY_URL, params=params, timeout=20) # make the GET request to the Google Places API with a timeout of 20 seconds
    r. raise_for_status() # raise an error if the request was not successful (e.g., if the API key is invalid or if there was a network issue)
    data = r.json() # parse the JSON response from the API


    results = [] # initialize an empty list to store the results
    for item in data.get("results", [])[:limit]: # iterate over the results from the API response, up to the specified limit
        loc = (item.get("geometry", {}).get("location", {}) or {} # get the location information from the API response, with a default of an empty dictionary if the expected keys are not present
               results.append({ # append a dictionary with the relevant information about each place to the results list
            "name": item.get("name"), # get the name of the place from the API response
            "address": item.get("vicinity") or "", # get the address of the place from the API response, with a default of an empty string if the expected key is not present
            "lat": loc.get("lat"),# get the latitude of the place from the location information, with a default of None if the expected key is not present
            "lng": loc.get("lng"), # get the longitude of the place from the location information, with a default of None if the expected key is not present
            "rating": item.get("rating"), # get the rating of the place from the API response, with a default of None if the expected key is not present
            "price_level": item.get("price_level"), # get the price level of the place from the API response, with a default of None if the expected key is not present
            "is_open_now": item.get("opening_hours") or {}).get("open_now"), # get the open_now status of the place from the opening_hours information, with a default of None if the expected keys are not present
            "provider_place_id": item.get("place_id", ""), # get the unique place ID from the API response, with a default of an empty string if the expected key is not present
            "provider": "google", # add a field to indicate that this place information is from the Google Places API
               }) # end of the dictionary being appended to the results list
    return results # return the list of results from the function

        
   
