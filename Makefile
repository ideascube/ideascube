# -- Development --------------------------------------------------------------
develop:
	pip3 install --no-use-wheel -r requirements-dev.txt

doc:
	mkdocs serve

dummydata: migrate
	python3 manage.py dummydata
	python3 manage.py reindex

migrate:
	python3 manage.py migrate --database=default
	python3 manage.py migrate --database=transient

upgrade-deps:
	pip-compile --rebuild --header --index --annotate --upgrade requirements.in
	pip-compile --rebuild --header --index --annotate --upgrade requirements-dev.in
	# Remove -e in the requirements.txt.
	# See issue : https://github.com/spotify/dh-virtualenv/issues/200
	sed -i 's/^-e //g' requirements.txt

sync-deps:
	pip-sync requirements-dev.txt

ci-images:
	docker build --file dockerfiles/ci-jessie-python34 --tag ideascube/ideascube-ci:jessie-python34 .
	docker push ideascube/ideascube-ci:jessie-python34
	
	docker build --file dockerfiles/ci-stretch-python35 --tag ideascube/ideascube-ci:stretch-python35 .
	docker push ideascube/ideascube-ci:stretch-python35


# -- Translations -------------------------------------------------------------
collect_translations:
	python3 manage.py makemessages --all --no-obsolete --ignore=debian -d django
	python3 manage.py makemessages --all --no-obsolete --ignore=debian -d djangojs

push_translations:
	tx push -s

pull_translations:
	tx pull --all --force

compile_translations:
	python3 manage.py compilemessages


# -- Testing ------------------------------------------------------------------
test:
	py.test

test-coverage:
	py.test --cov=ideascube/ --cov-report=term-missing --cov-fail-under=92

quality-check:
	py.test --flakes -m flakes

check-missing-migrations:
	python manage.py makemigrations
	git status --porcelain | grep -E '^\?\? ' && exit 1 || :

test-data-migration:
	set -e ; \
	git branch | grep -E '^\*'; \
	git log --oneline --graph --decorate --all | head -20; \
	BRANCH=$$CI_BUILD_REF_NAME; if [ -z $$BRANCH ]; then BRANCH=$$(git rev-parse --abbrev-ref HEAD); fi; \
	LATEST_TAG=$$(git describe --abbrev=0 --tags); \
	\
	echo "# Loading some data at $$LATEST_TAG"; \
	git checkout $$LATEST_TAG; \
	rm -fr storage; \
	make migrate; \
	python3 manage.py loaddata --database=default test-data/data.json; \
	python3 manage.py reindex; \
	\
	echo "# Running migrations on $$BRANCH"; \
	git checkout $$BRANCH; \
	git rev-parse HEAD; \
	git log --oneline --graph --decorate --all | head -20; \
	make migrate
	py.test --migrations
