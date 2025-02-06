from celery import Celery
from services.video_processor import VideoProcessor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Redis URL from environment variables, fallback to default if not set
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Initialize Celery
celery = Celery('video_translator',
             broker=REDIS_URL,
             backend=REDIS_URL)

# Configure Celery
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour timeout for tasks
)

@celery.task(bind=True)
def process_video_task(self, file_path: str, target_language: str, preserve_voice: bool = True):
    """Celery task for processing videos."""
    try:
        # Update task state to processing
        self.update_state(state='PROCESSING',
                         meta={'current': 'Starting video processing...',
                               'percent': 0})
        
        processor = VideoProcessor()
        
        # Update progress for audio extraction
        self.update_state(state='PROCESSING',
                         meta={'current': 'Extracting audio...',
                               'percent': 20})
        
        # Process the video
        result = processor.process_video(
            video_path=file_path,
            target_language=target_language,
            preserve_voice=preserve_voice
        )
        
        # Clean up the original file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return {
            'status': 'success',
            'result': result
        }
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return {
            'status': 'error',
            'error': str(e)
        }

@celery.task
def cleanup_task(file_path: str):
    """Clean up temporary files after processing."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        return {'status': 'success', 'message': f'Cleaned up {file_path}'}
    except Exception as e:
        return {'status': 'error', 'error': str(e)} 