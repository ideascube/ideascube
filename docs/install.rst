Installation
============


You need python 2.7 installed.

Install system dependencies::

    sudo apt-get install python-pip python-virtualenv virtualenvwrapper


Create a virtualenv (we name it `ideasbox` here but the name is up to you)::

    mkvirtualenv ideasbox


Install python dependencies::

    pip install -r requirements.txt


If you need to hack on the code, install dev dependencies::

    pip install -r requirements-dev.txt


Project setup
-------------

Dev setup
~~~~~~~~~

Run the initial database migration::

    python manage.py migrate


Production setup
~~~~~~~~~~~~~~~~

You need to define the place where you will store the application medias and
Sqlite files. Then you need to add the path as environment variable::

    export DATASTORAGE=/path/to/storage

You need to define the user model to be used, again through an environment
variable, for example::

    export AUTH_USER_MODEL=ideasbox.BurundiRefugeeUser

More on user model configuration in the :doc:`user model <user_model>` page.

Run the initial database migration::

    python manage.py migrate

