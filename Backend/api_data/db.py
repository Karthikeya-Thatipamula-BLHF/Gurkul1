from pymongo import MongoClient
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Secure MongoDB connection - NO HARDCODED CREDENTIALS
MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")

if not MONGO_URI:
    logger.error("❌ MongoDB URI not found in environment variables!")
    logger.error("Please set MONGODB_URI or MONGO_URI in your .env file")
    raise ValueError("MongoDB connection string not configured")

# Log connection attempt without exposing credentials
logger.info("🔌 Attempting MongoDB connection...")

# Connect to MongoDB with proper error handling
try:
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
        maxPoolSize=10,
        minPoolSize=1
    )

    # Test the connection
    client.admin.command('ping')
    logger.info("✅ MongoDB connection successful!")

except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    logger.error("Please check your MongoDB URI and network connectivity")
    raise

db = client["gurukul"]

# Define collections based on actual database structure
user_collection = db["user_data"]  # For storing chat messages
user_data_collection = db["User"]  # For storing user information
subjects_collection = db["subjects"]  # For storing subject information
lectures_collection = db["lectures"]  # For storing lecture information

# Keep these for backward compatibility
pdf_collection = db["pdf_collection"]
image_collection = db["image_collection"]
tests_collection = db["tests_collection"]

# Print available collections for debugging
print("\nCollections in database:")
try:
    for collection in db.list_collection_names():
        print(f" - {collection}")
except Exception as e:
    print(f"Error listing collections: {e}")
