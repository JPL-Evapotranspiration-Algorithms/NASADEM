PYTHON_VERSION ?= 3.14

PACKAGE_NAME = NASADEM
ENVIRONMENT_NAME = $(PACKAGE_NAME)

.PHONY: clean test CI build twine-upload dist install uninstall reinstall environment remove-environment repomix

clean:
	rm -rf *.o *.out *.log
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -f repomix-output.xml
	find . -type d -name "__pycache__" -exec rm -rf {} +

test:
	pytest -m "not integration"

CI:
	tox

build:
	python -m build

twine-upload:
	twine upload dist/*

dist:
	make clean
	make build
	make twine-upload

install:
	pip install -e .[dev]

uninstall:
	pip uninstall $(PACKAGE_NAME)

reinstall:
	make uninstall
	make install

environment:
	mamba create -y -n $(ENVIRONMENT_NAME) -c conda-forge python=$(PYTHON_VERSION)

remove-environment:
	mamba env remove -y -n $(ENVIRONMENT_NAME)

repomix:
	npx repomix --ignore "**/*.ipynb,**/*.hgt,**/*.tif,**/*.tiff,**/*.zip,debug/**" -o repomix-output.xml

show-issues:
	gh issue list --state open --json number,title,body --template '{{range .}}## #{{.number}}: {{.title}}{{"\n\n"}}{{.body}}{{"\n\n---\n\n"}}{{end}}'
