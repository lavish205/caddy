FROM ubuntu:14.04
MAINTAINER Lavish Aggarwal "lavish@zopper.com"

RUN apt-get update && apt-get -y upgrade && apt-get install -y git python2.7 python-pip python-dev libyaml-dev

ADD . /srv/
WORKDIR /srv/src/
RUN pip install -r requirements.txt
ADD config/docker/run.sh /usr/local/