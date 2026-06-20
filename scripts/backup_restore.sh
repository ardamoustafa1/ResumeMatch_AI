#!/usr/bin/env bash
set -e

# Load configuration from .env if exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-resumematch_ai}"
BACKUP_DIR="./backups"

# Ensure backup dir exists
mkdir -p "$BACKUP_DIR"

COMMAND=$1

case "$COMMAND" in
    backup)
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        BACKUP_FILE="${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql"
        echo "Creating database backup: ${BACKUP_FILE}..."
        docker compose exec -T postgres pg_dump -U $POSTGRES_USER -d $POSTGRES_DB -F c > "$BACKUP_FILE"
        echo "Backup completed successfully."
        ;;
    restore)
        BACKUP_FILE=$2
        if [ -z "$BACKUP_FILE" ]; then
            echo "Error: Please specify the backup file to restore."
            echo "Usage: $0 restore <backup_file>"
            exit 1
        fi
        if [ ! -f "$BACKUP_FILE" ]; then
            echo "Error: Backup file $BACKUP_FILE does not exist."
            exit 1
        fi
        echo "Restoring database from: ${BACKUP_FILE}..."
        
        echo "WARNING: This will overwrite existing data. Press Ctrl+C to cancel."
        sleep 3

        # Use pg_restore with clean flag (-c) instead of dropping the DB manually
        docker compose exec -T postgres pg_restore -U $POSTGRES_USER -d $POSTGRES_DB -c -1 < "$BACKUP_FILE"
        echo "Restore completed successfully."
        ;;
    *)
        echo "Usage: $0 {backup|restore <file>}"
        exit 1
        ;;
esac
