.PHONY: default test lint format

default: test format

test:
	py -3.8 -m pytest auto_derby

lint:
	py -3.8 ./scripts/run_pyright.py
	py -3.8 -m black -t py38 --check --diff .

format:
	py -3.8 -m black -t py38 . 

web:
	cd auto_derby/web/; pnpm run build
