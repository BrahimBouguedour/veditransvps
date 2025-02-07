import redis
from urllib.parse import urlparse

def test_redis():
    try:
        # Railway Redis URL
        redis_url = "redis://default:bckPtkWvVHzMYdnbOYExNBmNEJUmrTIc@roundhouse.proxy.rlwy.net:41753"
        
        # Parse the Redis URL
        parsed_url = urlparse(redis_url)
        
        # Create a Redis client with the Railway URL
        r = redis.Redis(
            host=parsed_url.hostname,
            port=parsed_url.port,
            password=parsed_url.password,
            ssl=True,  # Enable SSL for Railway connection
            ssl_cert_reqs=None  # Skip certificate verification
        )
        
        # Try to set a value
        r.set('test_key', 'Hello from Railway Redis!')
        
        # Try to get the value
        value = r.get('test_key')
        if value:
            print(f"Successfully retrieved value: {value.decode('utf-8')}")
        
        # Delete the test key
        r.delete('test_key')
        
        print("✅ Redis connection test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to Redis: {str(e)}")
        return False

if __name__ == "__main__":
    test_redis() 