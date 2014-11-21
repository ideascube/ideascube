doc:
	cd docs && make html
test:
	py.test --cov .
