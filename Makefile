test:
	py.test
install:
	pip install -r requirements.txt
devinstall:
	pip install -r requirements-dev.txt
doc:
	cd docs && make html
dummydata:
	python manage.py dummydata
collect_translations:
	python manage.py makemessages -a
push_translations:
	tx push -s
pull_translations:
	tx pull
compile_translations:
	python manage.py compilemessages
build:
	dpkg-buildpackage -us -uc
