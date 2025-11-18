from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
PASSING_PERCENT = int(os.getenv("PASSING_PERCENT", 70))
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", 3))
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
