from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime
import uuid
import json
from celery_app import process_video_task

app = FastAPI(title="Video Translation Platform API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class TranslationParams(BaseModel):
    source_language: Optional[str] = "auto"
    target_language: str
    preserve_voice: bool = True

class TranslationResponse(BaseModel):
    task_id: str
    status: str
    message: str

# Routes
@app.get("/")
async def read_root():
    return {"message": "Welcome to Video Translation Platform API"}

@app.post("/api/upload", response_model=TranslationResponse)
async def upload_video(
    video_file: UploadFile = File(...),
    translation_params: str = Form(...)
):
    try:
        # Parse translation parameters
        params = TranslationParams(**json.loads(translation_params))
        
        # Validate file format
        if not video_file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join("uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(video_file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await video_file.read()
            buffer.write(content)
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Start processing task
        process_video_task.delay(
            file_path,
            params.target_language,
            params.preserve_voice
        )
        
        return TranslationResponse(
            task_id=task_id,
            status="queued",
            message="Video upload successful. Processing started."
        )
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid translation parameters format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    try:
        # Get task result from Celery
        task = process_video_task.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            return {
                "task_id": task_id,
                "status": "queued",
                "progress": {
                    "step": "waiting",
                    "percentage": 0
                }
            }
        elif task.state == 'PROCESSING':
            return {
                "task_id": task_id,
                "status": "processing",
                "progress": task.info
            }
        elif task.state == 'SUCCESS':
            return {
                "task_id": task_id,
                "status": "completed",
                "result": task.get()
            }
        else:
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(task.info)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 