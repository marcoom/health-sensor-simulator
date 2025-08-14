FROM tiangolo/uvicorn-gunicorn:python3.11

ARG MODE

ENV MODE=${MODE}

COPY ./requirements/base.txt .
RUN pip install -r base.txt

COPY ./health_sensor_simulator /app
WORKDIR /app
