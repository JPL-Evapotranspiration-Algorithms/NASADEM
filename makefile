PYTHON_VERSION ?= 3.13

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
	pytest

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
	npx repomix --ignore "**/*.ipynb,**/*.hgt,**/*.tif,**/*.tiff,**/*.zip,debug/**" -o repomix-output.xml --copy


generate-history:
	fish -c ' \
		git fetch --tags --quiet; \
		set first_commit (git rev-list --max-parents=0 HEAD | head -n 1); \
		set releases (gh release list --limit 1000 --json tagName,createdAt --jq "sort_by(.createdAt) | .[].tagName"); \
		begin; \
			echo "========================================"; \
			echo "REPOSITORY RELEASE TIMELINE"; \
			echo "========================================"; \
			gh release list --limit 1000; \
			echo ""; \
			if test (count $$releases) -ge 1; \
				set first_rel $$releases[1]; \
				echo "========================================"; \
				echo "INITIAL COMMIT ($$first_commit) -> FIRST RELEASE ($$first_rel)"; \
				echo "========================================"; \
				git log --reverse --stat -p $$first_commit^..$$first_rel -- "*.py" "pyproject.toml"; \
				echo ""; \
			end; \
			if test (count $$releases) -ge 2; \
				for i in (seq 2 (count $$releases)); \
					set prev_idx (math $$i - 1); \
					set prev $$releases[$$prev_idx]; \
					set curr $$releases[$$i]; \
					echo "========================================"; \
					echo "RELEASE COMMIT HISTORY: $$prev -> $$curr"; \
					echo "========================================"; \
					git log --reverse --stat -p $$prev..$$curr -- "*.py" "pyproject.toml"; \
					echo ""; \
				end; \
			end; \
			if test (count $$releases) -ge 1; \
				set latest_rel $$releases[-1]; \
				echo "========================================"; \
				echo "LATEST RELEASE ($$latest_rel) -> CURRENT WORKING TREE (HEAD + UNCOMMITTED)"; \
				echo "========================================"; \
				git log --reverse --stat -p $$latest_rel..HEAD -- "*.py" "pyproject.toml"; \
				echo ""; \
				git status -s -- "*.py" "pyproject.toml"; \
				echo ""; \
				git diff HEAD -- "*.py" "pyproject.toml"; \
			else; \
				echo "========================================"; \
				echo "INITIAL COMMIT ($$first_commit) -> CURRENT WORKING TREE"; \
				echo "========================================"; \
				git log --reverse --stat -p -- "*.py" "pyproject.toml"; \
				echo ""; \
				git status -s -- "*.py" "pyproject.toml"; \
				echo ""; \
				git diff HEAD -- "*.py" "pyproject.toml"; \
			end; \
		end > release_diffs.patch; \
	'
