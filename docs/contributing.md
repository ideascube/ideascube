# Contributing to ideascube

Would you like to make the ideascube project better? Welcome! This document
will try to provide guidelines about what and how you can help.


## Contact and resources

If you have any question, problem or idea, feel free to get in touch with
project's maintainers:

* Chat using #ideascube channel on Freenode. If you are not familiar with
  [IRC](https://en.wikipedia.org/wiki/Internet_Relay_Chat), you can try
  this simple [online chat application](https://kiwiirc.com/client/irc.freenode.net/?nick=new-user|?#ideascube):
  just click "Start" then chat!

* Ask questions, report issues or propose ideas as
  [tickets](https://framagit.org/ideascube/ideascube/issues).

Here are online resources you may find useful to contribute to the project:

* Homepage: <http://www.ideas-box.org/>
* Code repository: <https://framagit.org/ideascube/ideascube/>
* Issues, questions and feature requests:
  <https://framagit.org/ideascube/ideascube/issues>
* Continuous integration: <https://framagit.org/ideascube/ideascube/pipelines>
* Documentation: <http://ideascube.readthedocs.org/>


## How can I give a hand?

* Join the brainstorming: report or comment issues; join the IRC channel
* Review [merge requests](https://framagit.org/ideascube/ideascube/merge_requests)
* Take an [issue](https://framagit.org/ideascube/ideascube/issues) and code :)
* What about a sprint?


## Install ideascube for development

### Setup system

Project's typical development environment requires:

* [Python 3.4 and above](https://www.python.org/)
* [Git](http://git-scm.com/)
* JPEG development headers (for Pillow).

On a Debian-based system, you may use:

    sudo apt-get install python3-pip python-virtualenv virtualenvwrapper python3-dev libjpeg-dev libxml2-dev libxslt1-dev zlib1g-dev build-essential autoconf automake libtool libdbus-glib-1-dev git
    sudo apt-get build-dep python3-dbus

### Download the source code

Get project's source code from
[project's code repository](https://framagit.org/ideascube/ideascube/)
(you may use your own fork):

    git clone git@framagit.org:ideascube/ideascube.git
    cd ideascube/

### Setup project

Create a virtualenv (we name it `ideascube` here but the name is up to you):

    mkvirtualenv ideascube

Install python dependencies:

    make develop

Run the initial database migration::

    make migrate

To populate the database with some initial dummy data, you can run the command::

    make dummydata

### Check and run!

Run the server:

    python3 manage.py runserver

Check it works:

    firefox http://localhost:8000

Done!
