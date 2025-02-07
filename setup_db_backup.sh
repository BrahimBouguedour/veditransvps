#!/bin/bash

# Create backup directories
sudo mkdir -p /var/backups/vedi-trans/postgres
sudo mkdir -p /var/backups/vedi-trans/redis
sudo chown -R ubuntu:ubuntu /var/backups/vedi-trans

# Create PostgreSQL backup script
cat > /home/ubuntu/backup_postgres.sh << EOF
#!/bin/bash
BACKUP_DIR="/var/backups/vedi-trans/postgres"
TIMESTAMP=\$(date +%Y%m%d_%H%M%S)
DATABASE="vedi_trans"

# Create backup
PGPASSWORD="your_strong_password" pg_dump -U vedi_user \$DATABASE > \$BACKUP_DIR/backup_\${DATABASE}_\${TIMESTAMP}.sql

# Keep only last 7 days of backups
find \$BACKUP_DIR -type f -mtime +7 -name "backup_*.sql" -delete
EOF

# Create Redis backup script
cat > /home/ubuntu/backup_redis.sh << EOF
#!/bin/bash
BACKUP_DIR="/var/backups/vedi-trans/redis"
TIMESTAMP=\$(date +%Y%m%d_%H%M%S)

# Create backup
redis-cli save
cp /var/lib/redis/dump.rdb \$BACKUP_DIR/redis_backup_\${TIMESTAMP}.rdb

# Keep only last 7 days of backups
find \$BACKUP_DIR -type f -mtime +7 -name "redis_backup_*.rdb" -delete
EOF

# Make scripts executable
chmod +x /home/ubuntu/backup_postgres.sh
chmod +x /home/ubuntu/backup_redis.sh

# Setup daily cron jobs for backups
(crontab -l 2>/dev/null; echo "0 3 * * * /home/ubuntu/backup_postgres.sh") | crontab -
(crontab -l 2>/dev/null; echo "0 4 * * * /home/ubuntu/backup_redis.sh") | crontab -

# Create restore script
cat > /home/ubuntu/restore_db.sh << EOF
#!/bin/bash

# Function to list backups
list_backups() {
    echo "PostgreSQL backups:"
    ls -l /var/backups/vedi-trans/postgres/
    echo -e "\nRedis backups:"
    ls -l /var/backups/vedi-trans/redis/
}

# Function to restore PostgreSQL
restore_postgres() {
    read -p "Enter PostgreSQL backup filename: " PG_BACKUP
    if [ -f "/var/backups/vedi-trans/postgres/\$PG_BACKUP" ]; then
        echo "Restoring PostgreSQL..."
        PGPASSWORD="your_strong_password" psql -U vedi_user vedi_trans < "/var/backups/vedi-trans/postgres/\$PG_BACKUP"
    else
        echo "Backup file not found!"
    fi
}

# Function to restore Redis
restore_redis() {
    read -p "Enter Redis backup filename: " REDIS_BACKUP
    if [ -f "/var/backups/vedi-trans/redis/\$REDIS_BACKUP" ]; then
        echo "Restoring Redis..."
        sudo systemctl stop redis
        sudo cp "/var/backups/vedi-trans/redis/\$REDIS_BACKUP" /var/lib/redis/dump.rdb
        sudo chown redis:redis /var/lib/redis/dump.rdb
        sudo systemctl start redis
    else
        echo "Backup file not found!"
    fi
}

# Main menu
echo "VediTrans Database Restore"
echo "1. List available backups"
echo "2. Restore PostgreSQL"
echo "3. Restore Redis"
echo "4. Exit"

read -p "Choose an option: " OPTION

case \$OPTION in
    1) list_backups ;;
    2) restore_postgres ;;
    3) restore_redis ;;
    4) exit 0 ;;
    *) echo "Invalid option" ;;
esac
EOF

chmod +x /home/ubuntu/restore_db.sh

echo "Backup system setup completed!"
echo "Daily backups will run at:"
echo "- PostgreSQL: 3 AM"
echo "- Redis: 4 AM"
echo "Use restore_db.sh to restore from backups" 