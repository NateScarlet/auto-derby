.PHONY: default test lint

default: test lint

test:
	py -3.8 -m pytest auto_derby

lint:
	py -3.8 -m black -t py38 --check . 
