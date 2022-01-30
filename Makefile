test-unit: check-virtual-env-activated
	python -m unittest discover -v . "*_test.py"
.PHONY: test-unit

typecheck: check-virtual-env-activated
	mypy . --exclude venv --strict --warn-unreachable --warn-return-any --disallow-untyped-calls
.PHONY: typecheck

requirements: check-virtual-env-activated
	pip3 install -r requirements.txt
.PHONY: requirements

test: test-unit typecheck
.PHONY: test

check-virtual-env-activated:
	@if [ -z "${VIRTUAL_ENV}" ]; then echo "You need to enable virtualenv before using this command";\
echo "source ./venv/bin/activate"; \
false;\
fi

pre-commit: test
.PHONY: pre-commit

install-dependencies: check-virtual-env-activated
	pip3 install -r requirements.txt
.PHONY: install-dependencies
