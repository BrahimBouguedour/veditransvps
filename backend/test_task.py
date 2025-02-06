from test_celery import add

# Submit a test task
result = add.delay(4, 4)
print("Task submitted. Task ID:", result.id)

# Wait for the result
print("Result:", result.get(timeout=10))  # Wait up to 10 seconds for the result 