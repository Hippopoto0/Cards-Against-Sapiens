FROM python


WORKDIR /app

RUN apt-get update

# RUN apt-get install python3.10

# RUN apt-get install python3-pip
RUN curl -sL https://deb.nodesource.com/setup_18.x

RUN apt-get -y install nodejs
RUN apt-get -y install npm

COPY server/requirements.txt ./

RUN pip install --no-input --requirement ./requirements.txt

COPY package*.json ./

RUN npm i

RUN npm i serve

COPY . .

EXPOSE 5173

EXPOSE 8000

# CMD python3 ./run.py

WORKDIR /app/frontend
RUN npm run build
WORKDIR /app

CMD cd /frontend/dist && serve -l tcp://0.0.0.0:5000

