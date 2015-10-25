# Installation

**Here are instructions to run a production environment**, i.e. tasks to
deploy, run and use an ideastube server.

**If you want to setup a development environment**, as an example in order to
contribute to the project, please see [Contributor guide](contributing.md).


## System setup

You need python 2.7 installed.

Install system dependencies:

    sudo apt-get install python-pip python-virtualenv virtualenvwrapper

Create a virtualenv (we name it `ideastube` here but the name is up to you):

    mkvirtualenv ideastube

Install python dependencies:

    make install  # for production


## Project setup

First, build the `.deb`:

    make build

Then install the `.deb`:

    make install

Create an administrator:

    sudo ideastube createsuperuser
