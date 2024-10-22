from pymongo import MongoClient
from datetime import datetime, timedelta
import hashlib
import json
import dotenv
import os
dotenv.load_dotenv()


class MongoCache:
    def __init__(self, connection_string=os.getenv('MONGO_URL'), db_name="search_cache"):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.cache = self.db.search_results
        
        # Create indexes for better query performance
        self.cache.create_index([("query_hash", 1)])
        self.cache.create_index([("timestamp", 1)])
        
        # Set cache expiration (24 hours by default)
        self.cache_expiration = timedelta(hours=24)
    
    def _generate_cache_key(self, **kwargs):
        """Generate a unique hash key for the search parameters"""
        # Sort kwargs to ensure consistent hash for same parameters
        sorted_kwargs = json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(sorted_kwargs.encode()).hexdigest()
    
    def get_cached_results(self, **kwargs):
        """Retrieve cached results if they exist and are not expired"""
        query_hash = self._generate_cache_key(**kwargs)
        cache_entry = self.cache.find_one({
            "query_hash": query_hash,
            "timestamp": {"$gt": datetime.utcnow() - self.cache_expiration}
        })
        
        if cache_entry:
            return cache_entry["results"]
        return None
    
    def cache_results(self, results, **kwargs):
        """Store results in cache with the current timestamp"""
        query_hash = self._generate_cache_key(**kwargs)
        
        self.cache.update_one(
            {"query_hash": query_hash},
            {
                "$set": {
                    "results": results,
                    "timestamp": datetime.utcnow(),
                    "parameters": kwargs
                }
            },
            upsert=True
        )
    
    def clear_expired_cache(self):
        """Remove expired cache entries"""
        self.cache.delete_many({
            "timestamp": {"$lt": datetime.utcnow() - self.cache_expiration}
        })
    
    def clear_cache(self):
        """Clear all cached results"""
        self.cache.delete_many({})

    def set_cache_expiration(self, hours=24):
        """Set cache expiration time"""
        self.cache_expiration = timedelta(hours=hours)