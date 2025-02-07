from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class ProcessingStatus(enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    videos = relationship("Video", back_populates="owner")

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    original_filename = Column(String)
    stored_filename = Column(String)
    file_size = Column(Integer)  # in bytes
    duration = Column(Float)  # in seconds
    format = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="videos")
    translations = relationship("Translation", back_populates="video")

class Translation(Base):
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    source_language = Column(String)
    target_language = Column(String)
    status = Column(String)  # Using ProcessingStatus enum values
    progress = Column(Float, default=0.0)  # 0-100
    error_message = Column(String, nullable=True)
    preserve_voice = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Output files
    translated_video_path = Column(String, nullable=True)
    subtitle_path = Column(String, nullable=True)
    transcript_path = Column(String, nullable=True)

    video = relationship("Video", back_populates="translations") 