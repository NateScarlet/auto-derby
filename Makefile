.PHONY: default test lint format

default: test format

test:
	py -3.8 -m pytest auto_derby

lint:
	PYTHONPATH=`py -3.8 -c 'import site; print(";".join(site.getsitepackages()))'` npx pyright --pythonversion 3.8 ./auto_derby/
	py -3.8 -m black -t py38 --check --diff .

format:
	py -3.8 -m black -t py38 . 
