#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check PostgreSQL status
check_postgres() {
    echo -e "${YELLOW}Checking PostgreSQL...${NC}"
    
    # Check if service is running
    if systemctl is-active --quiet postgresql; then
        echo -e "${GREEN}PostgreSQL service is running${NC}"
    else
        echo -e "${RED}PostgreSQL service is NOT running${NC}"
    fi
    
    # Check database size
    echo "Database sizes:"
    sudo -u postgres psql -c "\l+" | grep vedi_trans
    
    # Check connections
    echo -e "\nCurrent connections:"
    sudo -u postgres psql -c "SELECT datname, numbackends FROM pg_stat_database WHERE datname='vedi_trans';"
    
    # Check longest running queries
    echo -e "\nLongest running queries:"
    sudo -u postgres psql -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE state = 'active' AND query NOT LIKE '%pg_stat_activity%' ORDER BY duration DESC LIMIT 3;"
}

# Check Redis status
check_redis() {
    echo -e "\n${YELLOW}Checking Redis...${NC}"
    
    # Check if service is running
    if systemctl is-active --quiet redis-server; then
        echo -e "${GREEN}Redis service is running${NC}"
    else
        echo -e "${RED}Redis service is NOT running${NC}"
    fi
    
    # Get Redis info
    echo -e "\nRedis Info:"
    redis-cli info | grep -E "used_memory_human|connected_clients|connected_slaves|keyspace"
}

# Check disk space
check_disk() {
    echo -e "\n${YELLOW}Checking Disk Space...${NC}"
    df -h /var/lib/postgresql/
    echo -e "\nBackup directory space:"
    df -h /var/backups/vedi-trans/
}

# Main monitoring function
monitor() {
    clear
    echo "=== VediTrans Database Monitoring ==="
    echo "Time: $(date)"
    echo "=================================="
    
    check_postgres
    check_redis
    check_disk
    
    echo -e "\n${YELLOW}Last backup files:${NC}"
    ls -lh /var/backups/vedi-trans/postgres/ | tail -n 1
    ls -lh /var/backups/vedi-trans/redis/ | tail -n 1
}

# Run monitoring
if [ "$1" == "--watch" ]; then
    while true; do
        monitor
        echo -e "\nRefreshing in 30 seconds... (Press Ctrl+C to exit)"
        sleep 30
    done
else
    monitor
fi