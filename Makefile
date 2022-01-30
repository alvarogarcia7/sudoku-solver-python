test-unit: virtual_setup
	python -m unittest discover -v . "*_test.py"
.PHONY: test-unit

typecheck:
	mypy . --exclude venv --strict --warn-unreachable --warn-return-any --disallow-untyped-calls
.PHONY: typecheck

requirements: virtual_setup
	pip3 install -r requirements.txt
.PHONY: requirements

test: test-unit typecheck
.PHONY: test

virtual_setup:
	 . venv/bin/activate
.PHONY: virtual_setup

pre-commit: test
.PHONY: pre-commit

install-dependencies: virtual_setup
	pip3 install -r requirements.txt
.PHONY: install-dependencies
