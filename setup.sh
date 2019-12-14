sudo apt-get update -y; # patch linux
sudo apt-get install -y curl; sudo apt-get install -y unzip # install unix tools
sudo apt-get install -y mosquitto; sudo apt-get install -y mosquitto-clients # install MQTT tools
sudo apt-get install -y python3-pip;  sudo pip3 install paho-mqtt; sudo pip3 install geopy # install python tools
sudo apt install  -y docker.io; sudo systemctl start docker; sudo systemctl enable docker # install and start docker
sudo curl -L "https://github.com/docker/compose/releases/download/1.25.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose; sudo chmod +x /usr/local/bin/docker-compose # install docker compose
sudo service  mosquitto stop # stop MQTT - port conflict
sudo pip3 install redis # install redis cache tools
sudo apt install -y net-tools # install unix netwoking tools
sudo pip3 install pymongo; sudo apt install -y mongodb-clients # install mongodb tools
sudo docker build --tag mat-python-v1 .
sudo docker-compose down
sudo docker-compose up -d
