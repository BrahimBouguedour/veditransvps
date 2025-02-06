from database import engine
from models import Base
import os
from dotenv import load_dotenv

def init_db():
    load_dotenv()
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 