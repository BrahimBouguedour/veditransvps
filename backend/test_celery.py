from celery import Celery

# Initialize Celery
celery = Celery('test_app',
                broker='redis://localhost:6379/0',
                backend='redis://localhost:6379/0')

@celery.task
def add(x, y):
    return x + y 