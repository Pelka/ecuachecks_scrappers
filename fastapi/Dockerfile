FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install -r requirements.txt

COPY ./.env /code/.env

COPY ./app /code/app

CMD ["python3", "app/main.py"]
