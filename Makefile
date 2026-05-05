.PHONY: run test up down logs

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -q

up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200
