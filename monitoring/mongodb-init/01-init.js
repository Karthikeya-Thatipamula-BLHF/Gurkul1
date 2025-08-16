// MongoDB initialization script
// This script runs when MongoDB container starts for the first time

// Create application database
db = db.getSiblingDB('gurukul');

// Create collections with proper indexes
db.createCollection('users');
db.createCollection('memories');
db.createCollection('interactions');
db.createCollection('subjects');
db.createCollection('lessons');

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.memories.createIndex({ "user_id": 1, "persona_id": 1 });
db.memories.createIndex({ "timestamp": -1 });
db.interactions.createIndex({ "user_id": 1, "timestamp": -1 });
db.subjects.createIndex({ "name": 1 }, { unique: true });
db.lessons.createIndex({ "subject": 1, "topic": 1 });

print("MongoDB initialization completed successfully");
