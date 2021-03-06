FROM python:3.6-slim AS compile-image
RUN apt-get -y update
RUN apt-get install -y  --no-install-recommends build-essential gcc

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.6-slim AS build-image
COPY --from=compile-image /opt/venv /opt/venv

WORKDIR /app
COPY . .

ENV PATH="/opt/venv/bin:$PATH"
CMD gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8080 server.main:app