import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # API Keys
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
    
    # API URLs
    POKEMON_API_BASE_URL = "https://pokemon-tcg-api.p.rapidapi.com"
    
    # API Headers
    RAPIDAPI_HEADERS = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "pokemon-tcg-api.p.rapidapi.com"
    }
    
    # Application settings
    DEBUG = True