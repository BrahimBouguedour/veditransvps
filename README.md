# VediTrans - Video Translation Platform

A powerful web-based platform that translates videos by extracting speech, transcribing it, translating it into a selected language, and merging the translated audio back into the video.

## Features

- 🎥 Video upload with drag-and-drop support
- 🗣️ Speech extraction and transcription using OpenAI Whisper
- 🌐 Text translation using Google Translate API
- 🔊 Text-to-Speech using ElevenLabs API
- 🎯 Real-time processing status updates
- 📹 Support for multiple video formats (MP4, AVI, MOV, MKV)
- ⚡ Asynchronous processing with Celery
- 🔄 Background task management with Redis

## Prerequisites

- Python 3.8+
- Node.js 16+
- FFmpeg
- Redis (for task queue)

## Local Development Setup

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/vedi-trans.git
cd vedi-trans
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
cd backend
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
celery -A celery_app worker --loglevel=info
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

3. Set up environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

4. Start the development server:
```bash
npm run dev
```

## Ubuntu Server Deployment

### System Requirements
- Ubuntu 20.04 LTS or newer
- 2GB RAM minimum (4GB recommended)
- 20GB storage minimum

### Server Setup

1. Update system packages:
```bash
sudo apt update && sudo apt upgrade -y
```

2. Install system dependencies:
```bash
sudo apt install -y python3-pip python3-venv nodejs npm redis-server ffmpeg
```

3. Clone the repository:
```bash
git clone https://github.com/yourusername/vedi-trans.git
cd vedi-trans
```

4. Set up the backend:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. Set up environment variables:
```bash
cp .env.example .env
nano .env  # Edit with your configuration
```

6. Install PM2 for process management:
```bash
sudo npm install -g pm2
```

7. Create PM2 process files:

backend-app.json:
```json
{
  "apps": [{
    "name": "vedi-trans-api",
    "script": "uvicorn",
    "args": "main:app --host 0.0.0.0 --port 8000",
    "cwd": "./backend",
    "interpreter": "./venv/bin/python"
  }]
}
```

celery-worker.json:
```json
{
  "apps": [{
    "name": "vedi-trans-worker",
    "script": "celery",
    "args": "-A celery_app worker --loglevel=info",
    "cwd": "./backend",
    "interpreter": "./venv/bin/python"
  }]
}
```

8. Start the backend services:
```bash
pm2 start backend-app.json
pm2 start celery-worker.json
```

9. Set up the frontend:
```bash
cd frontend
npm install
npm run build
```

10. Install and configure Nginx:
```bash
sudo apt install -y nginx
```

Create Nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/vedi-trans
```

Add the configuration:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    # Frontend
    location / {
        root /path/to/vedi-trans/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/vedi-trans /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

11. Set up SSL with Certbot:
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
REDIS_URL=redis://localhost:6379/0
FRONTEND_URL=http://localhost:5173
```

Create a `.env.local` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

## Contributing

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions, please file an issue on the GitHub repository. 