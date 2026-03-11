run: build
	@docker run \
	    --rm \
		-ti \
	    messytables

build:
	@docker build -t messytables .

test:
	@uv run pytest

lint:
	@uv run ruff check .

format:
	@uv run ruff format .

.PHONY: run build test lint format
