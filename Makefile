# -- Development --------------------------------------------------------------
develop:
	pip3 install --no-use-wheel -r requirements-dev.txt

doc:
	mkdocs serve

dummydata: migrate
	python3 manage.py dummydata

migrate:
	python3 manage.py migrate --database=default
	python3 manage.py migrate --database=transient

upgrade-deps:
	pip-compile --rebuild --header --index --annotate  requirements.in
	pip-compile --rebuild --header --index --annotate  requirements-dev.in
	# Remove -e in the requirements(-dev).txt.
	# See issue : https://github.com/spotify/dh-virtualenv/issues/200
	sed -i 's/^-e //g' requirements.txt
	sed -i 's/^-e //g' requirements-dev.txt

sync-deps:
	pip-sync requirements-dev.txt


# -- Translations -------------------------------------------------------------
collect_translations:
	python3 manage.py makemessages --all --no-obsolete --ignore=debian -d django
	python3 manage.py makemessages --all --no-obsolete --ignore=debian -d djangojs

push_translations:
	tx push -s

pull_translations:
	tx pull --all

compile_translations:
	python3 manage.py compilemessages


# -- Testing ------------------------------------------------------------------
test:
	py.test

testcov:
	py.test --cov=ideascube/ --cov-report=term-missing --migrations
