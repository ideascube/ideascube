# Installation

**Here are instructions to run a production environment**, i.e. tasks to
deploy, run and use an ideascube server.

**If you want to setup a development environment**, as an example in order to
contribute to the project, please see [Contributor guide](contributing.md).


## System setup

You need python 2.7 installed.

First follow install process for [development](contributing.md).

Install system build dependencies:

    sudo apt-get install dh-virtualenv debhelper

Install test dependencies:

    make develop

First, build the `.deb`:

    make build

Then install the `.deb`:

    make install

Create an administrator:

    sudo ideascube createsuperuser
