install-hooks:
	rm .git/hooks/*
	cp .hooks/* .git/hooks
	chmod +x .git/hooks/*

install-editor-settings:
	mkdir -p .vscode
	rsync -a vscode-settings.json .vscode/settings.json

flake8:
	flake8 proxygen_cli scripts --config=tox.ini

pylint:
	pylint proxygen_cli scripts --rcfile=tox.ini

mypy:
	mypy proxygen_cli --exclude conftest.py --ignore-missing-imports

lint: flake8 pylint mypy

black-check:
	poetry run black proxygen_cli scripts --line-length=120 --check

black:
	poetry run black proxygen_cli scripts --line-length=120
