# Common commands. Everything runs through uv so the locked environment is always the one used.
.PHONY: setup test lint fmt status example figures paper-pull clean-example

setup:            ## create .venv from uv.lock (add --extra torch for the DL stack)
	uv sync

test:             ## unit tests (fast, CPU, no results needed)
	uv run pytest

lint:
	uv run ruff check .

fmt:
	uv run ruff format . && uv run ruff check --fix .

status:           ## research-loop gate table
	uv run research-loop status

example:          ## run the worked example end to end (seconds)
	uv run python scripts/run_experiment.py configs/toy_bandit.yaml
	uv run python scripts/make_figures.py

paper-pull:
	scripts/overleaf.sh pull

clean-example:    ## remove the worked example's outputs (runs/toy_bandit, runs/figures)
	rm -rf runs/toy_bandit runs/figures
