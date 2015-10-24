# Contributing to ideastube

Do you like to make the ideastube project better? Welcome! This document
will try to provide guidelines about what and how you can help.


## Contact and resources

If you have any question, problem or idea, feel free to get in touch with
project's maintainers:

* Chat using #ideastube channel on Freenode. If you are not familiar with
  [IRC](https://en.wikipedia.org/wiki/Internet_Relay_Chat), you can try
  this simple [online chat application](https://kiwiirc.com/client/irc.freenode.net/?nick=new-user|?#ideastube):
  just click "Start" then chat!

* Ask questions, report issues or propose ideas as
  [tickets](https://github.com/ideastue/ideastube/issues).

Here are online resources you may find useful to contribute to the project:

* Homepage: http://www.ideas-box.org/
* Code repository: https://github.com/ideastube/ideastube
* Issues, questions and feature requests:
  https://github.com/ideastube/ideastube/issues
* Continuous integration: https://travis-ci.org/ideastube/ideastube
* Documentation: https://github.com/ideastube/ideastube/blob/master/docs/index.md


## How can I give a hand?

* Join the brainstorming: report or comment issues; edit wiki; join IRC chan
* Review [pull requests](https://github.com/ideastube/ideastube/pulls)
* Take an [issue](https://github.com/ideastube/ideastube/issues) and code :)
* What about a sprint?


## Install ideastube for development

### Setup system

Project's typical development environment requires:

* [Python 2.7](https://www.python.org/)
* [Git](http://git-scm.com/)
* JPEG development headers (for Pillow).

On a Debian-based system, you may use:

    sudo apt-get install python-pip python-virtualenv virtualenvwrapper python-dev libjpeg-dev libxml2-dev libxslt1-dev

### Download the souce code

Get project's source code from
[project's code repository](https://github.com/ideastube/ideastube)
(you may use your own fork):

    git clone git@github.com:ideastube/ideastube.git
    cd ideastube/

### Setup project

Create a virtualenv (we name it `ideastube` here but the name is up to you):

    mkvirtualenv ideastube

Install python dependencies:

    make devinstall

Run the initial database migration::

    python manage.py migrate

To populate the database with some initial dummy data, you can run the command::

    make dummydata

### Check and run!

Run the server:

    python manage.py runserver

Check it works:

    firefox http://localhost:8000

Done!
