.PHONY: free-ports up down logs seed test

free-ports:
	@docker ps --filter "publish=27017" --format "{{.ID}} {{.Names}}" | awk '$$2 != "passa_o_bastao_mongodb" {print $$1}' | xargs -r docker stop
	@docker ps --filter "publish=8000" --format "{{.ID}} {{.Names}}" | awk '$$2 != "passa_o_bastao_backend" {print $$1}' | xargs -r docker stop

up: free-ports
	docker compose up --build --force-recreate -d

down:
	docker compose down

logs:
	docker compose logs -f

seed:
	PYTHONPATH=src .venv/bin/python3 -m infrastructure.persistence.seed

test:
	.venv/bin/pytest -v
