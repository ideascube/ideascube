# Installation

**Here are instructions to run a production environment**, i.e. tasks to
deploy, run and use an ideascube server.

**If you want to setup a development environment**, as an example in order to
contribute to the project, please see [Contributor guide](contributing.md).


## System setup

You need python 3.0 installed.

## Installation using ideascube repository (prefered)

Install software-properties-common

    sudo apt-get install software-properties-common

Install ideascube's repository

    sudo apt-add-repository 'deb http://repos.ideascube.org/debian/ jessie/'

Update your index

    sudo apt-get update

Upgrade your index

    sudo apt-get upgrade

Install ideascube

    sudo apt-get install ideascube

Create an administrator:

    sudo ideascube createsuperuser
    

## Installation using the build process

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
