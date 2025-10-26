"""
Test Redis connection
"""
import redis

print("Testing Redis connection...")
print("Connecting to: redis://localhost:6379/0")

try:
    r = redis.Redis(host='localhost', port=6379, db=0)
    response = r.ping()
    print(f"✓ Redis connection successful! Response: {response}")
    
    # Test setting and getting a value
    r.set('test_key', 'test_value')
    value = r.get('test_key')
    print(f"✓ Redis read/write working! Got value: {value.decode()}")
    r.delete('test_key')
    
except redis.ConnectionError as e:
    print(f"✗ Redis connection FAILED!")
    print(f"Error: {e}")
    print("\nTroubleshooting:")
    print("1. Is Redis running? Check the Redis terminal window")
    print("2. Is it running on port 6379?")
    print("3. Try restarting Redis")
except Exception as e:
    print(f"✗ Unexpected error: {e}")
