.PHONY: dev prod migrate worker test lint build qa logs shell down extension

dev:
	docker compose up --build

prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

migrate:
	docker compose exec api alembic -c backend/db/migrations/alembic.ini upgrade head

worker:
	celery -A backend.tasks.celery_app worker -Q high_priority --loglevel=info

test:
	pytest --cov=backend --cov-report=term-missing
	cd frontend && npm test

lint:
	ruff check backend tests scripts/register_user.py scripts/setup_mock_user.py
	ruff format --check backend tests scripts/register_user.py scripts/setup_mock_user.py
	mypy backend
	cd frontend && npm run lint
	cd frontend && npm run typecheck
	node --check extension/background.js
	node --check extension/content.js
	node --check extension/popup.js
	node --test tests/extension.test.mjs

build:
	cd frontend && npm run build
	docker compose build api frontend

qa: lint test build

logs:
	docker compose logs -f api worker frontend

shell:
	docker compose exec api /bin/bash

down:
	docker compose down

extension:
	@echo "Building Chrome extension zip..."
	@cd extension && zip -r ../resumematch-extension.zip . -x "*.DS_Store"
	@echo "Done! Load resumematch-extension.zip in Chrome."
