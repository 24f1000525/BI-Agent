import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.0-flash")
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))

# Application Configuration
APP_TITLE = os.getenv("APP_TITLE", "DataLens AI")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "Conversational AI for Instant Business Intelligence")

# Upload Configuration
MAX_FILE_SIZE_MB = 100  # Maximum file size in MB
ALLOWED_EXTENSIONS = {'.csv'}

# Session Configuration
CHAT_HISTORY_MAX_LENGTH = 20  # Maximum number of messages to keep in history
