
.PHONY: all pep8 test validate

all:
	@true

pep8:
	@echo "Run pep8 code checker"
	pep8 passwm/*.py

test:
	@echo "Run tests"
	python -m unittest discover -v


validate: pep8 test
