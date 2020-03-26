## -*- mode: make -*-

GIT = git
PYTHON = python

.PHONY: test dist distclean upload

clean:
	$(PYTHON) setup.py clean --all

test: clean
	$(PYTHON) -m pytest

dist: test
	$(PYTHON) setup.py sdist bdist_wheel
	$(PYTHON) -m twine check dist/*

upload_test: dist
	$(PYTHON) -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

upload: dist
	$(PYTHON) -m twine upload dist/*

# This is GNU specific I guess
VERSION = $(shell $(PYTHON) __about__.py)

TAG = v$(VERSION)

tag:
	git tag -a $(TAG) -m "$(TAG)"
	git push origin $(TAG)
