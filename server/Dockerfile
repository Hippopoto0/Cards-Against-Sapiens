FROM python

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

RUN mkdir server

COPY . server

EXPOSE 5000

CMD uvicorn server.main:app --reload --host 0.0.0.0 --port 5000