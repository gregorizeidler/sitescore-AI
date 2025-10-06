SHELL:=/bin/bash

.PHONY: up down logs backend frontend test test-cov seed gtfs metrics help clean

help:
	@echo "SiteScore AI - Makefile Commands"
	@echo ""
	@echo "Docker:"
	@echo "  make up           - Start all services"
	@echo "  make down         - Stop all services and remove volumes"
	@echo "  make logs         - Show backend logs"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo ""
	@echo "Data:"
	@echo "  make seed         - Seed database with sample projects"
	@echo "  make gtfs GTFS=/path/to/feed.zip  - Import GTFS data"
	@echo ""
	@echo "Shell Access:"
	@echo "  make backend      - Open bash in backend container"
	@echo "  make frontend     - Open shell in frontend container"
	@echo ""
	@echo "Monitoring:"
	@echo "  make metrics      - Show monitoring URLs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        - Remove generated files and cache"image.png

up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200 backend

backend:
	docker compose exec backend bash

frontend:
	docker compose exec frontend sh

test:
	docker compose exec backend pytest -v

test-cov:
	@echo "Running tests with coverage..."
	docker compose exec backend pytest --cov=app --cov-report=html --cov-report=term
	@echo ""
	@echo "Coverage report generated at: backend-python/htmlcov/index.html"

seed:
	docker compose exec backend python app/scripts/seed.py

gtfs:
	@if [ -z "$(GTFS)" ]; then \
		echo "❌ Error: GTFS path required"; \
		echo "Usage: make gtfs GTFS=/path/to/gtfs.zip"; \
		exit 1; \
	fi
	@echo "📦 Importing GTFS from: $(GTFS)"
	docker compose exec backend python app/scripts/ingest_gtfs.py --gtfs "$(GTFS)" --db "$${DATABASE_URL}"
	@echo "✅ GTFS import complete!"

metrics:
	@echo ""
	@echo "📊 Monitoring Dashboards:"
	@echo "  Prometheus: http://localhost:9090"
	@echo "  Grafana:    http://localhost:3001 (admin/admin)"
	@echo ""

clean:
	@echo "🧹 Cleaning generated files..."
	rm -rf backend-python/htmlcov
	rm -rf backend-python/.pytest_cache
	rm -rf backend-python/app/__pycache__
	find backend-python -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend-python -type f -name "*.pyc" -delete
	@echo "✅ Cleanup complete!"