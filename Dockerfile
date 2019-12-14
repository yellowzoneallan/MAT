FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install -y mosquitto
RUN apt-get install -y mosquitto-clients
RUN apt-get install -y python3-pip
RUN apt install -y mongodb-clients
RUN pip3 install paho-mqtt
RUN pip3 install geopy
RUN pip3 install redis
RUN pip3 install pymongo
COPY . /app
WORKDIR /app
EXPOSE 5555
CMD /usr/bin/python3 ./MAT-python-v1.py
