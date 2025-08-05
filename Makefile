# Raspberry Pi Day Planner - Makefile
# Provides convenient targets for development, testing, and deployment

.PHONY: help install install-dev test lint format clean build package deploy docker-build docker-run

# Default target
help:
	@echo "Raspberry Pi Day Planner - Available targets:"
	@echo ""
	@echo "Development:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  format       - Format code with black"
	@echo "  lint         - Run linting checks (flake8, mypy)"
	@echo "  test         - Run tests with pytest"
	@echo "  test-cov     - Run tests with coverage"
	@echo ""
	@echo "Building:"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  package      - Create distribution package"
	@echo ""
	@echo "Deployment:"
	@echo "  deploy       - Deploy to Raspberry Pi"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker container"
	@echo ""
	@echo "Utilities:"
	@echo "  status       - Show application status"
	@echo "  logs         - Show application logs"
	@echo "  backup       - Create backup of data"
	@echo "  restore      - Restore from backup"

# Installation targets
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

# Code quality targets
format:
	black .
	isort .

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
	mypy .

# Testing targets
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=modules --cov=main --cov-report=html --cov-report=term-missing

# Building targets
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

build: clean
	python -m build

package: build
	@echo "Package created in dist/ directory"

# Deployment targets
deploy:
	@echo "Deploying to Raspberry Pi..."
	@echo "1. Copy files to Raspberry Pi"
	@echo "2. Run installation script"
	@echo "3. Start service"
	@echo ""
	@echo "Manual steps:"
	@echo "  scp -r . pi@raspberrypi.local:/home/pi/raspberry-pi-day-planner/"
	@echo "  ssh pi@raspberrypi.local 'cd raspberry-pi-day-planner && ./install.sh'"

docker-build:
	docker build -t raspberry-pi-day-planner .

docker-run:
	docker run -d --name day-planner \
		--restart unless-stopped \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		-e DISPLAY=:0 \
		--device /dev/snd \
		raspberry-pi-day-planner

# Service management targets
status:
	@echo "Checking service status..."
	@systemctl status raspberry-pi-day-planner || echo "Service not found"

logs:
	@echo "Showing recent logs..."
	@journalctl -u raspberry-pi-day-planner -n 50 --no-pager

start:
	@echo "Starting service..."
	@sudo systemctl start raspberry-pi-day-planner

stop:
	@echo "Stopping service..."
	@sudo systemctl stop raspberry-pi-day-planner

restart:
	@echo "Restarting service..."
	@sudo systemctl restart raspberry-pi-day-planner

# Backup and restore targets
backup:
	@echo "Creating backup..."
	@mkdir -p backups
	@tar -czf backups/day-planner-backup-$$(date +%Y%m%d-%H%M%S).tar.gz \
		--exclude='*.pyc' \
		--exclude='__pycache__' \
		--exclude='.git' \
		--exclude='venv' \
		--exclude='backups' \
		.

restore:
	@echo "Available backups:"
	@ls -la backups/
	@echo ""
	@echo "To restore, run:"
	@echo "  tar -xzf backups/<backup-file>"

# Development utilities
dev-setup: install-dev
	@echo "Setting up development environment..."
	@mkdir -p tests data logs sounds reports
	@echo "Development environment ready!"

run-dev:
	@echo "Running in development mode..."
	@python main.py --debug

# Database management
db-info:
	@echo "Database information:"
	@python -c "from modules.logger import EventLogger; logger = EventLogger(); print(logger.get_database_info())"

db-export:
	@echo "Exporting database..."
	@python -c "from modules.logger import EventLogger; logger = EventLogger(); logger.export_data('data/export-$$(date +%Y%m%d).json', 'json')"

# System information
sys-info:
	@echo "System information:"
	@python -c "from modules.utils import get_system_info, is_raspberry_pi; import json; info = get_system_info(); info['is_raspberry_pi'] = is_raspberry_pi(); print(json.dumps(info, indent=2))"

# Quick test
quick-test:
	@echo "Running quick installation test..."
	@python test_installation.py

# All-in-one development target
dev: dev-setup format lint test
	@echo "Development environment ready and tests passed!"

# Production deployment check
prod-check: clean build test lint
	@echo "Production deployment check passed!" 