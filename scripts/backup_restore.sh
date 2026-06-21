#!/usr/bin/env bash
set -euo pipefail

if [[ -f .env ]]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
fi

POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-resumematch_ai}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
COMMAND="${1:-}"

require_encryption_password() {
    if [[ -z "${BACKUP_ENCRYPTION_PASSWORD:-}" ]]; then
        echo "BACKUP_ENCRYPTION_PASSWORD is required." >&2
        exit 1
    fi
}

mkdir -p "$BACKUP_DIR"
umask 077

case "$COMMAND" in
    backup)
        require_encryption_password
        timestamp="$(date -u +"%Y%m%dT%H%M%SZ")"
        backup_file="${BACKUP_DIR}/resumematch_${timestamp}.dump.enc"
        checksum_file="${backup_file}.sha256"

        docker compose exec -T postgres \
            pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -F c \
            | openssl enc -aes-256-cbc -salt -pbkdf2 \
                -pass env:BACKUP_ENCRYPTION_PASSWORD \
            > "$backup_file"

        shasum -a 256 "$backup_file" > "$checksum_file"
        echo "Encrypted backup created: $backup_file"
        ;;
    verify)
        require_encryption_password
        backup_file="${2:-}"
        if [[ ! -f "$backup_file" ]]; then
            echo "Backup file does not exist: $backup_file" >&2
            exit 1
        fi
        if [[ -f "${backup_file}.sha256" ]]; then
            shasum -a 256 -c "${backup_file}.sha256"
        fi
        openssl enc -d -aes-256-cbc -pbkdf2 \
            -pass env:BACKUP_ENCRYPTION_PASSWORD \
            -in "$backup_file" \
            | docker compose exec -T postgres pg_restore --list >/dev/null
        echo "Backup verified: $backup_file"
        ;;
    restore)
        require_encryption_password
        backup_file="${2:-}"
        if [[ ! -f "$backup_file" ]]; then
            echo "Backup file does not exist: $backup_file" >&2
            exit 1
        fi
        if [[ "${CONFIRM_RESTORE:-}" != "YES" ]]; then
            echo "Set CONFIRM_RESTORE=YES to authorize destructive restore." >&2
            exit 1
        fi
        "$0" verify "$backup_file"
        openssl enc -d -aes-256-cbc -pbkdf2 \
            -pass env:BACKUP_ENCRYPTION_PASSWORD \
            -in "$backup_file" \
            | docker compose exec -T postgres \
                pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists -1
        echo "Restore completed: $backup_file"
        ;;
    *)
        echo "Usage: $0 {backup|verify <file>|restore <file>}" >&2
        exit 1
        ;;
esac
