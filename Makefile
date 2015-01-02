all: init docs test

init:
	python setup.py develop
	pip install detox coverage Sphinx

test:
	coverage erase
	detox
	coverage html

docs: documentation

documentation:
	python setup.py build_sphinx
