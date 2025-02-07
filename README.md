# Video Translation Platform

A web-based platform that translates videos by extracting speech, transcribing it, translating it into a selected language, cloning the original speaker's voice, and merging the translated audio back into the video.

## Features

- Video upload with drag-and-drop support
- Speech extraction and transcription using OpenAI Whisper
- Text translation using Google Translate API
- Voice cloning using ElevenLabs API
- Automatic subtitle generation
- Real-time processing status updates
- Support for multiple video formats (MP4, AVI, MOV, MKV)

## Prerequisites

- Python 3.8+
- Node.js 16+
- FFmpeg
- Redis (for task queue)
- PostgreSQL

## Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

6. Start the Celery worker:
```bash
celery -A worker worker --loglevel=info
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

## Usage

1. Open your browser and navigate to `http://localhost:5173`
2. Upload a video file using the drag-and-drop interface
3. Select the target language for translation
4. Choose whether to preserve the original voice characteristics
5. Click "Upload and Translate" to start the process
6. Monitor the progress in real-time
7. Download the translated video and subtitles when processing is complete

## API Documentation

The API documentation is available at `http://localhost:8000/docs` when the backend server is running.

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
GOOGLE_CLOUD_PROJECT_ID=your_google_cloud_project_id
GOOGLE_APPLICATION_CREDENTIALS=path_to_your_google_credentials.json
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 