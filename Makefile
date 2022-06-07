.PHONY: default
default: test format

.PHONY: test
test:
	py -3.8 -m pytest auto_derby

.PHONY: link
lint:
	py -3.8 ./scripts/run_pyright.py
	py -3.8 -m black -t py38 --check --diff .
	py -3.8 ./scripts/run_cspell.py

.PHONY: format
format:
	py -3.8 -m black -t py38 . 

.PHONY: web
web:
	cd auto_derby/web/; pnpm run build
