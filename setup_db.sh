#!/bin/bash

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install PostgreSQL
echo "Installing PostgreSQL..."
sudo apt-get install -y postgresql postgresql-contrib

# Install Redis
echo "Installing Redis..."
sudo apt-get install -y redis-server

# Configure Redis
echo "Configuring Redis..."
sudo sed -i 's/supervised no/supervised systemd/' /etc/redis/redis.conf
sudo systemctl restart redis.service

# Configure PostgreSQL
echo "Configuring PostgreSQL..."
# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE vedi_trans;
CREATE USER vedi_user WITH PASSWORD 'your_strong_password';
ALTER ROLE vedi_user SET client_encoding TO 'utf8';
ALTER ROLE vedi_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE vedi_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE vedi_trans TO vedi_user;
\q
EOF

# Enable and start services
echo "Starting services..."
sudo systemctl enable postgresql
sudo systemctl start postgresql
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Create .env file with database credentials
echo "Creating .env file..."
cat > /home/ubuntu/vedi-trans/backend/.env << EOF
# Database Configuration
DATABASE_URL=postgresql://vedi_user:your_strong_password@localhost:5432/vedi_trans

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Other configurations from your existing .env file
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
GEMINI_API_KEY=your_gemini_api_key

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# File Upload Configuration
MAX_UPLOAD_SIZE=2147483648
UPLOAD_DIR=uploads
PROCESSED_DIR=processed

# Security
SECRET_KEY=your_secret_key_here_make_it_very_long_and_random
ALLOWED_ORIGINS=http://your_frontend_domain.com
EOF

# Set proper permissions
sudo chown ubuntu:ubuntu /home/ubuntu/vedi-trans/backend/.env
chmod 600 /home/ubuntu/vedi-trans/backend/.env

# Create required directories
mkdir -p /home/ubuntu/vedi-trans/backend/uploads
mkdir -p /home/ubuntu/vedi-trans/backend/processed
sudo chown -R ubuntu:ubuntu /home/ubuntu/vedi-trans/backend/uploads
sudo chown -R ubuntu:ubuntu /home/ubuntu/vedi-trans/backend/processed

# Print status
echo "Checking service status..."
sudo systemctl status postgresql
sudo systemctl status redis-server

echo "Setup completed!"
echo "Please update the .env file with your actual API keys and configurations."
echo "PostgreSQL database 'vedi_trans' created with user 'vedi_user'"
echo "Remember to change the default password in .env file!" 