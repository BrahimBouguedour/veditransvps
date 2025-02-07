import redis

# Railway Redis URL
redis_url = "redis://default:bckPtkWvVHzMYdnbOYExNBmNEJUmrTIc@roundhouse.proxy.rlwy.net:41753"

try:
    # Create Redis client
    r = redis.from_url(
        redis_url,
        ssl=True,
        ssl_cert_reqs=None
    )
    
    # Test connection with PING
    response = r.ping()
    print(f"Connection successful! PING response: {response}")
    
except Exception as e:
    print(f"Connection failed: {str(e)}") 