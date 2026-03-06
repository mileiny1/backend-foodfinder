from django.core.cache import cache # Import cache framework
from rest_framework.decorators import api_view, permission_classes # Import decorators for API views and permissions
from rest_framework.permissions import IsAuthenticated, AllowAny # Import permission class for authenticated users
from rest_framework.response import Response # Import Response class for API responses
from rest_framework import status # Import status codes for API responses


from .serializers import RegisterSerializer, FoodSearchSerializer # Import serializers for user registration and food search
from .models import FoodSearch, RestaurantResult # Import models for food search and restaurant results
from .services.ai_openai import expand_food_query # Import service for expanding food search queries using OpenAI
from .services.geo import haversine_m # Import service for calculating distance using the Haversine formula
from .services.places_router import search_places # Import service for searching places using Google Places API

@api_view(['GET']) # Define a view for health check
@permission_classes([AllowAny]) # Allow any user to access this view
def health(request): # Define a simple health check endpoint
    return Response({'ok' : True}, status=status.HTTP_200_OK) # Return a JSON response indicating the service is healthy

@api_view(['POST']) # Define a view for user registration
@permission_classes([AllowAny]) # Allow any user to access this view
def register(request): # Define a view for user registration
    s = RegisterSerializer(data=request.data) # Create an instance of the RegisterSerializer with the incoming request data
    s.is_valid(raise_exception=True) # Validate the data and raise an exception if it's invalid
    users = s.save() # Save the new user to the database
    return Response({'id': users.id, 'username': users.username, 'email': users.email}, status=status.HTTP_201_CREATED) # Return a JSON response with the new user's details and

@api_view(['POST']) # Define a view for food search
@permission_classes([IsAuthenticated]) # Require the user to be authenticated to access this view
def food_search(request): # Define a view for performing a food search
    """
    POST /api/food-search/
    Body:
    {
        "query": "pizza",
        "lat": 37.7749,
        "lng": -122.4194,
        "provider": "yelp"|"google",
        "radius_m": 5000,
        "limit":10,
        "min_rating": 4.2,
        "open_now": true,
        "price_range": [1, 2]
        
    }
    """
    query = (request.data.get("query")or "").strip() # Get the search query from the request data and remove any leading/trailing whitespace.
    

    if not query or lat is None or lng is None: # Check if the required parameters are present in the request
        return Response({'error': 'query, lat, and lng are required fields.'}, status=status.HTTP_400_BAD_REQUEST) # Return a JSON response indicating the missing fields

    lat = float(lat) # Convert latitude to a float
    lng = float(lng) # Convert longitude to a float
    provider =  (request.data.get("provider") or "").strip().lower() or None # Get the provider from the request data, convert it to lowercase and remove any leading/trailing whitespace
    radius_m = int(request.data.get("radius_m") or 3000) # Get the search radius from the request data, default to 3000 meters if not provided.
    limit = int(request.data.get("limit") or 10) # Get the limit for the number of results from the request data, default to 10 if not provided.
    min_rating = request.data.get("min_rating") # Get the minimum rating from the request data
    min_rating = float(min_rating) if min_rating is not None else None # Get the minimum rating from the request data and convert it to a float if it's provided
    open_now = request.data.get("open_now") # Get the open_now flag from the request data
    open_now = True if open_now is True else (False if open_now is False else None) # Convert the open_now flag to a boolean if it's provided.
    price_range = (request.data.get("price_range") or "").strip() or None  # Get the price range from the request data.
    expanded_terms = expand_food_query(query) # Use the OpenAI service to expand the search query into related terms
    cache_key = (
        f"places:{provider or 'default'}:{lat:.5f}:{lng:.5f}:"
        f"{radius_m}:{limit}:{min_rating}:{open_now}:{price_range}:"
        f"{'|'.join(expanded_terms)}"
    )
    cached = cache.get(cache_key) # Check if the search results are already cached for the given parameters.
    search = FoodSearch.objects.create(
        user = request.user,
        query=query,
        user_lat = lat,
        user_lng = lng,
        provider = (provider or "default"),
        expanded_terms = expanded_terms,
        filters = {
            "radius_m": radius_m,
            "limit": limit,
            "min_rating": min_rating,
            "open_now": open_now,
            "price_range": price_range
        }
    ) 
    if cached:
        for row in cached:
            RestaurantResult.objects.create(search=search, **row)
            return Response(FoodSearchSerializer(search).data, status=status.HTTP_201_CREATED)# Return the cached search results as a JSON response.
        merged = {}
        for terms in expanded_terms:
            hits = search_places(
                provider = provider,
                lat = lat,
                lng = lng, 
                radius_m = radius_m,
                open_now = open_now,
                prices_range = price_range,
                limit = 50,
            ) # Perform a search for places using the Google Places API with the given parameters and expanded search terms.
            for h in hits:
                pid = h.get("provider_place_id") or f"{h.get('name')} | {h.get('address')}"
                if h.get("lat") is not None and h.get("lng") is not None:
                    h["distance_m"] = haversine_m(lat,lng, h["lat"],h["lng"])
                else: 
                    h["distance_m"] = None
                if min_rating is not None and (h.get("rating") is None or float(h.get("rating")) < min_rating):
                    continue
                if open_now is True and h.get("is_open_now") is False:
                    continue 
                if pid not in merged:
                    merged[pid] = h
                else:
                    prev = merged[pid]
                    prev_d = prev.get("distance_m") if prev.get("distance_m") is not None else 10 ** 12
                    new_d = h.get("distance_m") if h.get("distance_m") is not None else 10 ** 12
                    if new_d < prev_d:
                        merged[pid] = h

    final = list(merged.values())
    final.sort(key=lambda x: (x.get("distance_m") if x.get("distance_m") is not None else 10 ** 12, -(x.get("rating") or 0.0))) 
    final = final[:limit]
    to_cache = []
    for h in final:
        row = {
            "name":h.get("name") or "",
            "address" : h.get("address") or "",
            "lat": h.get("lat"),
            "lng": h.get("lng"),
            "distance_m": h.get("distance_m"),
            "rating": h.get("rating"),
            "price_level": h.get("price_level"),
            "is_open_now": h.get("is_open_now"),
            "provider_place_id": h.get("provider_place_id") or "",
            "provider": h.get("provider") or "unknown"
        }
        RestaurantResult.objects.create(search = search, **row)
        to_cache.append(row)
    cache.set(cache_key, to_cache, timeout=60*10) # Cache the search results for 1 hour using the generated cache key.
    return Response(FoodSearchSerializer(search).data, status=status.HTTP_201_CREATED) # Return the search results as a JSON response.

@api_view(['GET']) # Define a view for retrieving search history.
@permission_classes([IsAuthenticated]) # Require the user to be authenticated to access this view.
def my_search_history(request): # Define a view for retrieving the authenticated user's search history.
    limit = int(request.query_params.get("limit") or 20) # Get the limit for the number of search history records to return from the query parameters, default to 20 if not provided.
    qs = FoodSearch.objects.filter(user = request.user).order_by("-created_at")[:limit] # Query the FoodSearch model for the authenticated user's search history, ordered by creation date in descending order, and limited to the specified number of records.
    return Response({"count": qs.count(), "items": FoodSearchSerializer(qs, many=True).data}, status=status.HTTP_200_OK) # Return the search history as a JSON response, including the count of records and the serialized data for each search.

   

  


                    
                
                




    


  











    