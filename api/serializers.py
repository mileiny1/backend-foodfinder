from django.contrib.auth.models import User # Importing the User model from Django's built-in authentication system.
from rest_framework import serializers # Importing the serializers module from Django REST Framework
from .models import FoodSearch, FoodSearch,RestaurantResult # Importing the FoodSearch and RestaurantResult models from the current app's models.

class RegisterSerializer(serializers.ModelSerializer): 
    password = serializers.CharField(write_only=True, min_length=6)  # Defining a password field that is write-only (not included in serialized output)

class Meta:
        model = User # Specifying that this serializer is for the User model
        fields = ('id', 'email', 'username', 'password') # Specifying the fields to be included in the serialized output
        def create(self, validated_data): # Overriding the create method to handle user creation with password hashing
              user = User(username=validated_data['username'], email=validated_data['email','']) # Creating a new User instance with the provided username and email.
              user.set_password(validated_data['password']) # Setting the user's password using Django's built-in method to ensure it is hashed.
              user.save() # Saving the user instance to the database
              return user # Returning the created user instance
        
        class RestaurantResultSerializer(serializers.ModelSerializer): # Serializer for the RestaurantResult model
              class Meta:
                    model = RestaurantResult # Specifying that this serializer is for the RestaurantResult model
                    fields = (
                        'id', 'name', 'address', 'lat', 'lng', 'distance_m', 'rating', 'price_level', 
                        'is_open_now', 'provider_places_id', 'provider'
                    ) # Including all fields from the RestaurantResult model in the serialized output

                    class FoodSearchSerializer(serializers.ModelSerializer): # Serializer for the FoodSearch model.
                            results = RestaurantResultSerializer(many=True, read_only=True) # Nested serializer for the related RestaurantResult objects
    
                            class Meta:
                                    model = FoodSearch # Specifying that this serializer is for the FoodSearch model
                                    fields = (
                                        'id', 'user', 'query', 'user_lat', 'user_lng', 'provider', 
                                        'expanded_terms', 'filters', 'created_at', 'results'
                                    ) # Including all fields from the FoodSearch model and the nested results in the serialized output
                 
            

            
              
       
   
