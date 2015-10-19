# Contributing to ideasbox.lan

Do you like to make the ideasbox.lan project better? Welcome! This document
will try to provide guidelines about what and how you can help.


## Contact and resources

If you have any question, problem or idea, feel free to get in touch with
project's maintainers:

* Chat using #ideasbox channel on Freenode. If you are not familiar with
  [IRC](https://en.wikipedia.org/wiki/Internet_Relay_Chat), you can try
  this simple [online chat application](https://kiwiirc.com/client/irc.freenode.net/?nick=new-user|?#ideasbox):
  just click "Start" then chat!

* Ask questions, report issues or propose ideas as
  [tickets] (https://github.com/issues).

Here are online resources you may find useful to contribute to the project:

* Homepage: http://www.ideas-box.org/
* Code repository: https://github.com/ideas-box/ideasbox.lan
* Issues, questions and feature requests:
  https://github.com/ideas-box/ideasbox.lan/issues
* Continuous integration: https://travis-ci.org/ideas-box/ideasbox.lan
* Documentation:

  * docs: https://github.com/ideas-box/ideasbox.lan/blob/master/docs/index.md
  * wiki: https://github.com/ideas-box/ideasbox.lan/wiki


## How can I give a hand?

* Join the brainstorming: report or comment issues; edit wiki; join IRC chan
* Review [pull requests](https://github.com/ideas-box/ideasbox.lan/pulls)
* Take an [issue](https://github.com/ideas-box/ideasbox.lan/issues) and code :)
* What about a sprint?


## Install ideasbox.lan for development

### Setup system

Project's typical development environment requires:

* [Python 2.7](https://www.python.org/)
* [Git](http://git-scm.com/)

On a Debian-based system, you may use:

    sudo apt-get install python-pip python-virtualenv virtualenvwrapper

### Download the souce code

Get project's source code from
[project's code repository](https://github.com/ideas-box/ideasbox.lan)
(you may use your own fork):

    git clone git@github.com:ideas-box/ideasbox.lan.git
    cd ideasbox.lan/

### Setup project

Create a virtualenv (we name it `ideasbox` here but the name is up to you):

    mkvirtualenv ideasbox

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
