# Release Process

So you want to release a new version, great!

First, make sure all the desired pull requests have been merged.

Next, pull [the latest translations](translate.md).

Finally, here are the steps to follow.

## Get a clean environment

Create a new virtual environment (`pew` makes this trivial), then get the code:

    $ pew mktmpenv -p python3
    $ git clone ssh://git@github.com/ideascube/ideascube
    $ cd ideascube
    $ git checkout master

Now install all the dependencies:

    $ make develop

## Sanity check

Run the tests:

    $ py.test

And run the migrations:

    $ python manage.py migrate --database=default
    $ python manage.py migrate --database=transient

Let's make sure there are no migration conflicts:

    $ rm -fr storage
    $ git checkout $TAG_FOR_LATEST_RELEASE
    $ python manage.py migrate --database=default
    $ python manage.py migrate --database=transient
    $ make dummydata
    $ git checkout master
    $ python manage.py migrate --database=default
    $ python manage.py migrate --database=transient

Ideally, in the above steps, it would be even better to use a real-world
database (from a server running the latest release) instead of the dummy data.

## Release

First, decide what the new version will be. Is it a new major, minor or patch
release?

At the moment, since we are still in the pre-1.0 days, we usually follow this
convention:

* if the release introduces new features, bump the **minor** version;
* if the release only fixes bugs, adds config files, then bump the **patch**
    version.

Write the `debian/changelog` entry for the new version. Review all the commits
in master since the last release to make sure you don't forget anything.

Bump the version in `ideascube/__init__.py`.

Commit, using the new version as the commit message:

    $ git commit -a -m "x.x.x"

Create a new tag named after the new version:

    $ git tag x.x.x

Push the release:

    $ git push origin master x.x.x

Make yourself a drink while you wait for Buildbot to finish building the Debian
packages. Follow its progress at http://buildbot.ideascube.org/waterfall
