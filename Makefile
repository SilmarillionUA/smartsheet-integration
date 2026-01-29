.PHONY: format

format:
	docker exec smartsheet-app-django-1 poetry run ruff format .
	docker exec smartsheet-app-django-1 poetry run isort .
	docker exec smartsheet-app-frontend-1 npx prettier --write "src/**/*.{js,jsx}"
