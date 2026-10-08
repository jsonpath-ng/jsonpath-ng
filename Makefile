OK_COLOR=\033[32;01m
NO_COLOR=\033[0m

all: lint unit

export PYTHONPATH:=${PWD}/src
version=`python -c 'import jsonpath_ng; print(jsonpath_ng.__version__)'`
filename=jsonpath_ng-`python -c 'import jsonpath_ng; print(jsonpath_ng.__version__)'`.tar.gz

apidocs:
	@sphinx-apidoc -f --follow-links -H "API documentation" -o docs/source src/jsonpath_ng

htmldocs:
	@rm -rf docs/_build
	$(MAKE) -C docs html

install:
	@pip install -e . --group dev

lint:
	@echo "$(OK_COLOR)==> Linting code ...$(NO_COLOR)"
	@prek run -a

test: clean
	@echo "$(OK_COLOR)==> Running tests ...$(NO_COLOR)"
	@tox

tag:
	@echo "$(OK_COLOR)==> Creating tag $(version) ...$(NO_COLOR)"
	@git tag -a "v$(version)" -m "Version $(version)"
	@echo "$(OK_COLOR)==> Pushing tag $(version) to origin ...$(NO_COLOR)"
	@git push origin "v$(version)"

bump:
	@bumpversion --commit --tag --current-version $(version) patch src/jsonpath_ng/__init__.py --allow-dirty

bump-minor:
	@bumpversion --commit --tag --current-version $(version) minor src/jsonpath_ng/__init__.py --allow-dirty

history:
	@git changelog --tag $(version)

clean:
	@echo "$(OK_COLOR)==> Cleaning up files that are already in .gitignore...$(NO_COLOR)"
	@git clean -Xf

publish:
	@echo "$(OK_COLOR)==> Releasing package ...$(NO_COLOR)"
	@python -m build
	@twine upload dist/*
	@rm -fr build dist .egg pook.egg-info
