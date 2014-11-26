test:
	py.test
install:
	pip install -r requirements.txt
devinstall:
	pip install -r requirements-dev.txt
doc:
	cd docs && make html
