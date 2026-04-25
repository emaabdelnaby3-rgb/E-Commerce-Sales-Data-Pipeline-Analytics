.PHONY: up down backend-test backend-compile

up:
	docker compose up --build

down:
	docker compose down

backend-test:
	cd backend && python -m pytest -q

backend-compile:
	cd backend && python -m compileall app run.py
