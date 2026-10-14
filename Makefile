.PHONY: bootstrap test server ready smoke dataset

bootstrap:
	uv sync --frozen

test:
	uv run python -m unittest discover -s unit_tests -v
	uv run python scripts/validate_task.py

server:
	./scripts/start_opensandbox_server.sh

ready:
	./scripts/wait_for_opensandbox.sh

smoke:
	./scripts/run_opensandbox_smoke.sh

dataset:
	uv run harbor add tasks/day1-smoke --to datasets/day1-dev

