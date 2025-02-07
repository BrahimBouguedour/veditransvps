#!/bin/bash

# Update system
sudo apt-get update
sudo apt-get install -y python3.9 python3.9-venv python3-pip ffmpeg git build-essential python3.9-dev

# Create project directory
mkdir -p /home/ubuntu/vedi-trans
cd /home/ubuntu/vedi-trans

# Clone the repository (you'll need to update this URL)
git clone https://github.com/servici/vedi-trans.git .

# Setup Python virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
cd backend
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Setup systemd service
sudo tee /etc/systemd/system/vedi-trans.service << EOF
[Unit]
Description=VediTrans FastAPI Application
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/vedi-trans/backend
Environment="PATH=/home/ubuntu/vedi-trans/venv/bin"
Environment="PYTHONPATH=/home/ubuntu/vedi-trans/backend"
ExecStart=/home/ubuntu/vedi-trans/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
EOF

# Setup Celery service
sudo tee /etc/systemd/system/vedi-trans-celery.service << EOF
[Unit]
Description=VediTrans Celery Worker
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/vedi-trans/backend
Environment="PATH=/home/ubuntu/vedi-trans/venv/bin"
Environment="PYTHONPATH=/home/ubuntu/vedi-trans/backend"
ExecStart=/home/ubuntu/vedi-trans/venv/bin/celery -A celery_app worker --loglevel=info

[Install]
WantedBy=multi-user.target
EOF

# Start and enable services
sudo systemctl daemon-reload
sudo systemctl start vedi-trans
sudo systemctl enable vedi-trans
sudo systemctl start vedi-trans-celery
sudo systemctl enable vedi-trans-celery

# Print status
echo "Deployment completed!"
echo "Checking services status..."
sudo systemctl status vedi-trans
sudo systemctl status vedi-trans-celery 