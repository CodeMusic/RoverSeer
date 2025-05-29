#!/bin/bash

# Variables
#CONTAINER_NAME="redmine-docker_db_1"
CONTAINER_NAME="redmine_db_1"
DB_NAME="redmine"
DB_USER="redmine"
DB_PASS="xunjmq84"
BACKUP_DIR="$HOME/redmine-docker/backups"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
FILENAME="redmine_db_backup_$TIMESTAMP.sql"

# Create backup
docker exec "$CONTAINER_NAME" \
  mysqldump -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" > "$BACKUP_DIR/$FILENAME"

# Optional: remove backups older than 7 days
find "$BACKUP_DIR" -type f -name "*.sql" -mtime +7 -exec rm {} \;

echo "✅ Backup saved to: $BACKUP_DIR/$FILENAME"
