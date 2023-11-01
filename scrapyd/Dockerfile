FROM python:3.8.18-alpine3.18

ENV PYTHONUNBUFFERED 1

RUN set -ex && apk --no-cache --virtual .build-deps add build-base g++ bash curl gcc libgcc tzdata psutils supervisor linux-headers openssl-dev postgresql-dev libffi-dev libxml2-dev libxslt-dev

RUN ln -sf /usr/share/zoneinfo/America/Mexico_City /etc/localtime

RUN echo "America/Mexico_City" > /etc/timezone

RUN python -m pip install --upgrade pip

COPY ./requirements.txt /

RUN pip install -r requirements.txt

RUN mkdir /etc/scrapyd

RUN mkdir -p /scrapyd/logs

COPY scrapyd.conf /etc/scrapyd/

COPY supervisord.conf /etc/

VOLUME /scrapyd

EXPOSE 6800

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
