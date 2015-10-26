test:
	py.test
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
	-mv builds/ideastube_* builds/old
build:
	mkdir -p builds && dpkg-buildpackage -us -uc -Ibuilds && mv ../ideastube_* builds/
install:
	sudo dpkg -i builds/*.deb
uninstall:
	sudo dpkg -r ideastube
