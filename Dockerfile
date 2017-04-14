FROM debian:jessie

RUN echo 'deb-src http://ftp.debian.org/debian/ jessie main' >> /etc/apt/sources.list
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python3-pip python3-dev libjpeg-dev libxml2-dev libxslt1-dev zlib1g-dev build-essential autoconf automake libtool libdbus-glib-1-dev git
RUN apt-get build-dep -y python3-dbus

ADD . /usr/src/app

WORKDIR /usr/src/app

RUN make develop
RUN python3 manage.py migrate && \
    make dummydata

EXPOSE 8000

ENTRYPOINT ["python3"]
CMD ["manage.py", "runserver", "0.0.0.0:8000"]
