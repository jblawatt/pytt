#!/bin/env make

run:
	venv/bin/python -m pytt display times.pytt


watch:
	watch venv/bin/python -m pytt display times.pytt


sync:
	venv/bin/pip-compile
	venv/bin/pip-sync
