

__init__.py: *.png __init__.py.gotmpl
	# http://github.com/NateScarlet/gotmpl
	ls *.png | jq -nR 'reduce inputs as $$item ([]; . + [$$item]) | { Files: . }' | gotmpl -o $@ __init__.py.gotmpl
