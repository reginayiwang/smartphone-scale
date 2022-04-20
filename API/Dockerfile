FROM python:3.8-slim

WORKDIR /

COPY . .

ENV PORT=$port

RUN apt-get update && apt-get install -y --no-install-recommends apt-utils \
    && apt-get install -y gcc \
    && apt-get install -y libopenblas-dev \
    && apt-get install -y libharminv-dev

RUN pip install pip --upgrade \
    && pip install -r requirements.txt

RUN pip install pharminv

EXPOSE $PORT

CMD gunicorn --bind 0.0.0.0:$PORT api:app