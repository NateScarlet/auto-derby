__init__.py: *.png __init__.py.gotmpl
	# http://github.com/NateScarlet/gotmpl v0.2.0
	ls *.png | jq -nR 'reduce inputs as $$item ([]; . + [$$item]) | { Files: . }' | gotmpl -i - -o $@ __init__.py.gotmpl
	py -3.8 -m black -t py38 $@


%.pos.png:
	magick convert $@ -depth 1 $@

	