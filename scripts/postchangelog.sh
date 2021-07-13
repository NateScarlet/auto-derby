#!/bin/bash

# https://github.com/conventional-changelog/standard-version/issues/317
sed -r -e 's/^#{1,3} \[/## [/' -i CHANGELOG.md
npx prettier --write CHANGELOG.md
