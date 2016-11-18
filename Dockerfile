FROM continuumio/anaconda:4.2.0
MAINTAINER Eric Sage <eric.david.sage@gmail.com>

ADD . /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN python setup.py install

EXPOSE 5000

CMD ["diffusiond"]
