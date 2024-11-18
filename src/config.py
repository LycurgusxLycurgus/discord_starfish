# src/config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Discord Bot Token
    DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    
    # OpenAI API Key
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Bot Username (as mentioned in Discord)
    BOT_USERNAME = os.getenv('BOT_USERNAME', 'fwog-ai')
    
    # AI Model to use
    AI_MODEL = os.getenv('AI_MODEL', 'hf:google/gemma-2-9b-it')
