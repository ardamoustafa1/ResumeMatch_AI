.PHONY: dev prod migrate worker test logs shell

dev:
	docker compose up --build

prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

migrate:
	docker compose exec api alembic -c backend/db/migrations/alembic.ini upgrade head

worker:
	celery -A backend.tasks.celery_app worker --loglevel=info

test:
	docker compose exec api pytest

logs:
	docker compose logs -f api worker

shell:
	docker compose exec api /bin/bash
