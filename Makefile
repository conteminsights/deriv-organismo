up:
	docker compose up -d

down:
	docker compose down

test:
	uv run pytest
