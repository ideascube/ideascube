test:
	py.test
install:
	pip install -r requirements.txt
devinstall:
	pip install -r requirements-dev.txt
doc:
	mkdocs serve
dummydata:
	python manage.py dummydata
collect_translations:
	python manage.py makemessages -a --ignore=debian
	python manage.py makemessages -d djangojs -a --ignore=debian
push_translations:
	tx push -s
pull_translations:
	tx pull
compile_translations:
	python manage.py compilemessages
build:
	dpkg-buildpackage -us -uc
