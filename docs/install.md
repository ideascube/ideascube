# Installation


You need python 2.7 installed.

Install system dependencies:

    sudo apt-get install python-pip python-virtualenv virtualenvwrapper


Create a virtualenv (we name it `ideasbox` here but the name is up to you):

    mkvirtualenv ideasbox


Install python dependencies:

    make install  # for production
    # or
    make devinstall  # for hacking on the code



## Project setup

### Dev setup

Run the initial database migration::

    python manage.py migrate

To populate the database with some initial dummy data, you can run the command::

    python manage.py dummydata


### Production setup

First, build the `.deb`:

    make build

Then install the `.deb`:

    sudo dpkg -i ../path/to/package.deb

Run the initial database migration:

    sudo ideasbox migrate

Create an administrator:

    sudo ideasbox createsuperuser

