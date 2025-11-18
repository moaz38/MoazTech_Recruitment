from pymongo import MongoClient
import os # <-- Zaroori hai
# import config (REMOVED)

# === VIP DEPLOYMENT FIX ===
# Render.com ke liye Environment Variables istemal karein
# Hum ab 'config.py' ki jagah direct 'os.environ.get()' use kar rahe hain
# (Defaults aapki .env file se li hain, taake local bhi chale)
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://muhammadmoaz087_db_user:moaz123%23@cluster0.m037hgd.mongodb.net/?retryWrites=true&w=majority')
DB_NAME = os.environ.get('DB_NAME', 'moaztech_db')
# === END FIX ===

# ===========================
# MongoDB Connection
# ===========================
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    # Test connection
    client.server_info()
    print("MongoDB Connection Successful")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    # Fallback to a local/dummy DB if connection fails (optional)
    client = MongoClient("mongodb://localhost:27017/")
    db = client["fallback_db"]

# ===========================
# Collections
# ===========================
users_col = db['users']          # User info
quizzes_col = db['quizzes']      # Quiz questions
results_col = db['results']      # Quiz results
messages_col = db['messages']    # Messages sent to admin