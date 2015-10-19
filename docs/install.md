# Installation

**Here are instructions to run a production environment**, i.e. tasks to
deploy, run and use an ideasbox.lan server.

**If you want to setup a development environment**, as an example in order to
contribute to the project, please see [Contributor guide]
(https://github.com/ideas-box/ideasbox.lan/CONTRIBUTING.md).


## System setup

You need python 2.7 installed.

Install system dependencies:

    sudo apt-get install python-pip python-virtualenv virtualenvwrapper

Create a virtualenv (we name it `ideasbox` here but the name is up to you):

    mkvirtualenv ideasbox

Install python dependencies:

    make install  # for production


## Project setup

First, build the `.deb`:

    make build

Then install the `.deb`:

    sudo dpkg -i ../path/to/package.deb

Run the initial database migration:

    sudo ideasbox migrate

Create an administrator:

    sudo ideasbox createsuperuser
