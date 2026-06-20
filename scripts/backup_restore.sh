#!/usr/bin/env bash
set -e

# Configuration
POSTGRES_CONTAINER="networkforge-db-1"
POSTGRES_USER="user"
POSTGRES_DB="resumematch"
BACKUP_DIR="./backups"

# Ensure backup dir exists
mkdir -p "$BACKUP_DIR"

COMMAND=$1

case "$COMMAND" in
    backup)
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        BACKUP_FILE="${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql"
        echo "Creating database backup: ${BACKUP_FILE}..."
        docker exec -t $POSTGRES_CONTAINER pg_dump -U $POSTGRES_USER -d $POSTGRES_DB -F c > "$BACKUP_FILE"
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
        # First drop existing connections, then drop db, recreate, and restore
        docker exec -i $POSTGRES_CONTAINER psql -U $POSTGRES_USER -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${POSTGRES_DB}' AND pid <> pg_backend_pid();"
        docker exec -i $POSTGRES_CONTAINER psql -U $POSTGRES_USER -d postgres -c "DROP DATABASE IF EXISTS ${POSTGRES_DB}; CREATE DATABASE ${POSTGRES_DB};"
        docker exec -i $POSTGRES_CONTAINER pg_restore -U $POSTGRES_USER -d $POSTGRES_DB -1 < "$BACKUP_FILE"
        echo "Restore completed successfully."
        ;;
    *)
        echo "Usage: $0 {backup|restore <file>}"
        exit 1
        ;;
esac
