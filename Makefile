test:
	py.test
testcov:
	py.test --cov=ideascube/ --cov-report=term-missing
develop:
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
clean:
	-mv builds/ideascube_* builds/old
build:
	mkdir -p builds && dpkg-buildpackage -us -uc -Ibuilds && mv ../ideascube_* builds/
install:
	sudo dpkg -i builds/*.deb
uninstall:
	sudo dpkg -r ideascube
