FROM debian:wheezy

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python-pip python-virtualenv virtualenvwrapper python-dev libjpeg-dev libxml2-dev libxslt1-dev zlib1g-dev build-essential gettext

ADD . /usr/src/app

WORKDIR /usr/src/app

RUN pip install --upgrade pip
RUN make develop
RUN python manage.py migrate && \
    make dummydata
RUN make compile_translations

EXPOSE 8000

ENTRYPOINT ["python"]
CMD ["manage.py", "runserver", "0.0.0.0:8000"]
