FROM python:3.8.18-alpine3.18

ENV PYTHONUNBUFFERED 1

RUN set -ex && apk --no-cache --virtual .build-deps add build-base g++ bash curl gcc libgcc tzdata psutils supervisor linux-headers openssl-dev postgresql-dev libffi-dev libxml2-dev libxslt-dev

RUN ln -sf /usr/share/zoneinfo/America/Mexico_City /etc/localtime

RUN echo "America/Mexico_City" > /etc/timezone

RUN python -m pip install --upgrade pip

RUN pip install scrapydweb psycopg2

RUN mkdir /scrapydweb
COPY scrapydweb_settings_v10.py /scrapydweb/
WORKDIR /scrapydweb/

EXPOSE 5000

ENTRYPOINT ["scrapydweb"]