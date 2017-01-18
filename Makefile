test:
	py.test
testcov:
	py.test --cov=ideascube/ --cov-report=term-missing --migrations
develop:
	pip3 install -r requirements-dev.txt
doc:
	mkdocs serve
dummydata: migrate
	python3 manage.py dummydata
collect_translations:
	python3 manage.py makemessages --all --no-obsolete --ignore=debian -d django
	python3 manage.py makemessages --all --no-obsolete --ignore=debian -d djangojs
push_translations:
	tx push -s
pull_translations:
	tx pull
compile_translations:
	python3 manage.py compilemessages
clean:
	-mv builds/ideascube_* builds/old
build:
	mkdir -p builds && dpkg-buildpackage -us -uc -Ibuilds && mv ../ideascube_* builds/
install:
	sudo dpkg -i builds/*.deb
uninstall:
	sudo dpkg -r ideascube
migrate:
	python3 manage.py migrate --database=default
	python3 manage.py migrate --database=transient
