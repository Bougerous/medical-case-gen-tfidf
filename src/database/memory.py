"""
Memory module for storing conversation history and case details using Redis.
"""
import json
import time
import datetime
from typing import Dict, List, Optional
import redis
from loguru import logger

from src.config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD


# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        return super().default(obj)


class RedisMemory:
    """Redis-based memory for storing conversation history and case details."""
    
    def __init__(self):
        """Initialize Redis connection."""
        try:
            self.redis = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True
            )
            self.redis.ping()  # Test connection
            logger.info("Connected to Redis server")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            logger.warning("Using fallback in-memory storage")
            self.redis = None
            self.fallback_storage = {}
    
    def save_case_scenario(self, user_id: str, case_data: Dict) -> bool:
        """
        Save case scenario to Redis.
        
        Args:
            user_id: User identifier
            case_data: Case scenario data
            
        Returns:
            True if successful, False otherwise
        """
        key = f"case:{user_id}"
        try:
            if self.redis:
                case_data["updated_at"] = time.time()
                # Use the custom encoder to handle datetime objects
                self.redis.set(key, json.dumps(case_data, cls=DateTimeEncoder))
            else:
                self.fallback_storage[key] = case_data
                self.fallback_storage[key]["updated_at"] = time.time()
            return True
        except Exception as e:
            logger.error(f"Error saving case scenario: {e}")
            return False
    
    def get_case_scenario(self, user_id: str) -> Optional[Dict]:
        """
        Get case scenario from Redis.
        
        Args:
            user_id: User identifier
            
        Returns:
            Case scenario data or None if not found
        """
        key = f"case:{user_id}"
        try:
            if self.redis:
                data = self.redis.get(key)
                return json.loads(data) if data else None
            else:
                return self.fallback_storage.get(key)
        except Exception as e:
            logger.error(f"Error retrieving case scenario: {e}")
            return None
    
    def save_chat_history(self, user_id: str, messages: List[Dict]) -> bool:
        """
        Save chat history to Redis.
        
        Args:
            user_id: User identifier
            messages: List of message dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        key = f"chat:{user_id}"
        try:
            if self.redis:
                self.redis.set(key, json.dumps(messages, cls=DateTimeEncoder))
            else:
                self.fallback_storage[key] = messages
            return True
        except Exception as e:
            logger.error(f"Error saving chat history: {e}")
            return False
    
    def get_chat_history(self, user_id: str) -> List[Dict]:
        """
        Get chat history from Redis.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of message dictionaries
        """
        key = f"chat:{user_id}"
        try:
            if self.redis:
                data = self.redis.get(key)
                return json.loads(data) if data else []
            else:
                return self.fallback_storage.get(key, [])
        except Exception as e:
            logger.error(f"Error retrieving chat history: {e}")
            return []
    
    def save_user_data(self, user_id: str, user_data: Dict) -> bool:
        """
        Save user data to Redis.
        
        Args:
            user_id: User identifier
            user_data: User data
            
        Returns:
            True if successful, False otherwise
        """
        key = f"user:{user_id}"
        try:
            if self.redis:
                self.redis.set(key, json.dumps(user_data, cls=DateTimeEncoder))
            else:
                self.fallback_storage[key] = user_data
            return True
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
            return False
    
    def get_user_data(self, user_id: str) -> Optional[Dict]:
        """
        Get user data from Redis.
        
        Args:
            user_id: User identifier
            
        Returns:
            User data or None if not found
        """
        key = f"user:{user_id}"
        try:
            if self.redis:
                data = self.redis.get(key)
                return json.loads(data) if data else None
            else:
                return self.fallback_storage.get(key)
        except Exception as e:
            logger.error(f"Error retrieving user data: {e}")
            return None
    
    def get_status(self) -> Dict:
        """Get the status of the memory system."""
        if self.redis:
            try:
                info = self.redis.info()
                return {
                    "status": "connected",
                    "backend": "redis",
                    "version": info.get("redis_version", "unknown"),
                    "memory_used": info.get("used_memory_human", "unknown")
                }
            except Exception as e:
                return {
                    "status": "error",
                    "backend": "redis",
                    "error": str(e)
                }
        else:
            return {
                "status": "fallback",
                "backend": "in-memory",
                "keys": len(self.fallback_storage)
            }