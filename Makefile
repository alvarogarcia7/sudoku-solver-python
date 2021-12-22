test-unit: virtual_setup
	python -m unittest discover -v
.PHONY: test-unit

typecheck:
	echo "mypy still not configured"
.PHONY: typecheck

requirements: virtual_setup
	pip3 install -r requirements.txt
.PHONY: requirements

test: typecheck test-unit
.PHONY: test

virtual_setup:
	 . venv/bin/activate
.PHONY: virtual_setup

pre-commit: test
.PHONY: pre-commit
