.PHONY: test default


default:

test:
	py -3.8 -m pytest auto_derby -s
