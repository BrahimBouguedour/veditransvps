#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to check step completion
check_step() {
    read -p "$1 (y/n): " answer
    if [[ $answer == "y" ]]; then
        echo -e "${GREEN}✓ Done${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ Pending${NC}"
        return 1
    fi
}

clear
echo "=== VediTrans Deployment Checklist ==="
echo "Follow these steps in order:"

echo -e "\n${YELLOW}1. Server Setup${NC}"
check_step "  1.1. Have you created an Ubuntu server (20.04 or newer)?"
check_step "  1.2. Can you SSH into the server?"
check_step "  1.3. Do you have sudo access?"

echo -e "\n${YELLOW}2. Domain Setup${NC}"
check_step "  2.1. Do you have a domain name?"
check_step "  2.2. Have you pointed your domain to the server IP?"
check_step "  2.3. Have you configured SSL (will be done with Certbot)?"

echo -e "\n${YELLOW}3. Environment Variables${NC}"
echo "Prepare these values before proceeding:"
echo "  - OPENAI_API_KEY"
echo "  - ELEVENLABS_API_KEY"
echo "  - GEMINI_API_KEY"
echo "  - Database password"
check_step "  3.1. Do you have all API keys ready?"

echo -e "\n${YELLOW}4. Deployment Commands${NC}"
echo "Run these commands on your server:"
echo "1. Update system and install Git:"
echo "   sudo apt-get update && sudo apt-get upgrade -y"
echo "   sudo apt-get install -y git"
echo ""
echo "2. Clone repository:"
echo "   git clone https://github.com/servici/vedi-trans.git"
echo "   cd vedi-trans"
echo ""
echo "3. Run database setup:"
echo "   sudo ./setup_db.sh"
echo ""
echo "4. Setup backups:"
echo "   sudo ./setup_db_backup.sh"
echo ""
echo "5. Update environment variables:"
echo "   nano backend/.env"
echo ""
echo "6. Run deployment:"
echo "   sudo ./deploy.sh"
echo ""
echo "7. Install and configure Nginx:"
echo "   sudo apt-get install -y nginx"
echo "   sudo nano /etc/nginx/sites-available/vedi-trans"
echo ""
echo "8. Create Nginx configuration:"
cat << 'EOF'
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF
echo ""
echo "9. Enable site and install SSL:"
echo "   sudo ln -s /etc/nginx/sites-available/vedi-trans /etc/nginx/sites-enabled/"
echo "   sudo apt-get install -y certbot python3-certbot-nginx"
echo "   sudo certbot --nginx -d your_domain.com"
echo ""
echo "10. Monitor deployment:"
echo "    ./monitor_db.sh --watch"

echo -e "\n${YELLOW}5. Post-Deployment${NC}"
echo "Verify these points:"
check_step "  5.1. Can you access the frontend website?"
check_step "  5.2. Is the API responding?"
check_step "  5.3. Are the database backups running?"
check_step "  5.4. Is SSL working correctly?"

echo -e "\n${YELLOW}6. Monitoring Setup${NC}"
check_step "  6.1. Have you tested the monitoring script?"
check_step "  6.2. Have you tested database backups?"
check_step "  6.3. Have you tested the restore process?"

echo -e "\n${YELLOW}Deployment Notes:${NC}"
echo "1. Keep your .env file secure and backed up"
echo "2. Monitor the logs using: sudo journalctl -u vedi-trans -f"
echo "3. Check service status: sudo systemctl status vedi-trans"
echo "4. Database backups are in: /var/backups/vedi-trans/"
echo "5. Use monitor_db.sh to check system health"

echo -e "\n${YELLOW}Support Commands:${NC}"
echo "- Restart application: sudo systemctl restart vedi-trans"
echo "- View logs: sudo journalctl -u vedi-trans -f"
echo "- Monitor databases: ./monitor_db.sh --watch"
echo "- Backup now: sudo ./backup_postgres.sh && sudo ./backup_redis.sh"
echo "- Restore backup: sudo ./restore_db.sh" 