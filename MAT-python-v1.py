#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Allan MacLean
# Python Part of MAT Challenge - Dec 2019

import paho.mqtt.subscribe as subscribe # add MQTT tools
import paho.mqtt.client as mqttClient # add MQTT tools
import json # add json<>python object tools
from geopy.distance import geodesic # add gps tools
from datetime import datetime # add timestamp tools
import time # add time tools
import redis  # add redis tools
import pymongo  # add mongo tools
import urllib.parse # used when testing mongo authentication
import os # used to obtain hostname for mqtt client id

cars_in_race = 6 # reduce the hardcoding, revisit positions list
origin = (52.06813447551777,  -1.023626530253432431) # random point on track - eventually startline
topics = ['#'] # set topic to listen to
now = datetime.now() # get current timestamp
racedata = [] # setup empty list, current race data in memory, each car has it's own list within
positions = [0,1,2,3,4,5] # setup list, current race positions data in memory
oldpositions = [0,0,0,0,0,0]  # setup empty list, to be used to detect overtakes
rediscar=[0,0,0,0,0] # setup empty list - redis
newtimestamp = float(datetime.timestamp(now) / 1000.0) # get current timestamp - redis
tracklat = 52.06813447551777 # random point on track - eventually startline - redis
tracklong = -1.023626530253432431 # random point on track - eventually startline -redis
totaldistance = 0 # setup empty distance - redis
r = redis.Redis() # initialise the redis cache

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection
    else:
        print("Connection failed")

def redis_get_positions(fname): # fetch position data from redis cache
  fname[0] = int(r.get("position0"))
  fname[1] = int(r.get("position1"))
  fname[2] = int(r.get("position2"))
  fname[3] = int(r.get("position3"))
  fname[4] = int(r.get("position4"))
  fname[5] = int(r.get("position5"))

def redis_put_positions(fname):# update position data to redis cache
  r.mset({"position0": positions[0], "position1": fname[1], "position2": fname[2], "position3": fname[3], "position4": fname[4], "position5": fname[5]})

def redis_put_cardata(fname):# update car data to redis cache
  if fname == 0:
      r.mset({"timestamp0": newtimestamp, "lat0": tracklat, "long0": tracklong, "totaldistance0": totaldistance})
  if fname == 1:
      r.mset({"timestamp1": newtimestamp, "lat1": tracklat, "long1": tracklong, "totaldistance1": totaldistance})
  if fname == 2:
      r.mset({"timestamp2": newtimestamp, "lat2": tracklat, "long2": tracklong, "totaldistance2": totaldistance})
  if fname == 3:
      r.mset({"timestamp3": newtimestamp, "lat3": tracklat, "long3": tracklong, "totaldistance3": totaldistance})
  if fname == 4:
      r.mset({"timestamp4": newtimestamp, "lat4": tracklat, "long4": tracklong, "totaldistance4": totaldistance})
  if fname == 5:
      r.mset({"timestamp5": newtimestamp, "lat5": tracklat, "long5": tracklong, "totaldistance5": totaldistance})

def redis_get_car(fname): # car data from redis cache
  if carno == 0:
      fname[0] = int(0)
      fname[1] = float(r.get("timestamp0"))
      fname[2] = float(r.get("lat0"))
      fname[3] = float(r.get("totaldistance0"))
      fname[4] = float(r.get("long0"))
  if carno == 1:
      fname[0] = 1
      fname[1] = float(r.get("timestamp1"))
      fname[2] = float(r.get("lat1"))
      fname[3] = float(r.get("totaldistance1"))
      fname[4] = float(r.get("long1"))
  if carno == 2:
      fname[0] = 2
      fname[1] = float(r.get("timestamp2"))
      fname[2] = float(r.get("lat2"))
      fname[3] = float(r.get("totaldistance2"))
      fname[4] = float(r.get("long2"))
  if carno == 3:
      fname[0] = 3
      fname[1] = float(r.get("timestamp3"))
      fname[2] = float(r.get("lat3"))
      fname[3] = float(r.get("totaldistance3"))
      fname[4] = float(r.get("long3"))
  if carno == 4:
      fname[0] = 4
      fname[1] = float(r.get("timestamp4"))
      fname[2] = float(r.get("lat4"))
      fname[3] = float(r.get("totaldistance4"))
      fname[4] = float(r.get("long4"))
  if carno == 5:
      fname[0] = 5
      fname[1] = float(r.get("timestamp5"))
      fname[2] = float(r.get("lat5"))
      fname[3] = float(r.get("totaldistance5"))
      fname[4] = float(r.get("long5"))

def on_message(client, userdata, message):
    print("Message received: ",  message.payload)
    cardata = json.loads(message.payload) # convert current message from JSON
    mydict = { "carIndex": (cardata["carIndex"]), "latitude": (cardata["location"].get("lat")), "longitude": (cardata["location"].get("long")), "timestamp": (cardata["timestamp"])} # convert message to mongo schema
    x = mycol.insert_one(mydict) # write message to mondo db
    carno = int(cardata["carIndex"]) # extract car number from message
    newtimestamp = (cardata["timestamp"]/1000.0) # extract timestamp from message and adjust value for processing
    tracklat = float(cardata["location"].get("lat")) # extract currrent gps
    tracklong = float(float(cardata["location"].get("long"))) # extract currrent gps
    trackgps = (float(cardata["location"].get("lat")),float(cardata["location"].get("long"))) # extract currrent gps
    oldinfo = redis_get_car(rediscar) # obtain last saved data for current car
    # print(oldinfo, rediscar, carno, "fetched oldinfo from redis, rediscar, carno")
    oldgps = (rediscar[2], rediscar[4]) # last known gps for current car
    olddistance = rediscar[3] # last known total distance for current car
    oldtimestamp = rediscar[1] # last known timestamp for current car
    olddate = datetime.fromtimestamp(oldtimestamp) # calculate date of last timestamp
    newdate = datetime.fromtimestamp(newtimestamp) # calculate date of last timestamp
    tripdistance = geodesic(oldgps, trackgps).kilometers # calculate delta distance
    timedifference = newdate - olddate  # calculate time delta
    totaldistance = olddistance + tripdistance # calculate new total race distance
    timediffmicro = timedifference.microseconds # convert time delta to micro s
    speed = (tripdistance * 1000000 * 3600 / timediffmicro) # calculate current speed
    newinfo = [carno,newtimestamp,trackgps,totaldistance] # prep current values for saving
    if carno == 0:
        redis_get_positions(positions)
        racedistance = positions
        print(positions)
        leaderdistance = sorted(racedistance, key=float, reverse=True) # order total distance
        for raceorder in range(cars_in_race): # revisit in case more efficient mthond
            for distances in range(cars_in_race):
                if racedistance[raceorder] == leaderdistance[distances] and leaderdistance != 0:
                    positions[distances] = raceorder # calculate race order on total distance
        for positionorder in range(cars_in_race):
            positiondata = {"timestamp": int(newtimestamp * 1000), "carIndex": positionorder, "type": "POSITION", "value": (positions[positionorder] + 1)} # prep position message
            positionmessage = json.dumps(positiondata) # convert into JSON:
            client.publish("carStatus", positionmessage) # send mqtt message
            print(positionmessage)
        if positions != oldpositions: # check for overtakes
            eventdata = {"timestamp": int(newtimestamp * 1000), "text": "overtake detected"} # prep event message
            eventmessage = json.dumps(eventdata) # convert into JSON:
            client.publish("events", eventmessage) # send mqtt message
            redis_put_positions(positions) # update positions in redis
            print(eventmessage)
    redis_put_cardata(carno) # save updated data for current car
    speeddata = {"timestamp": int(newtimestamp * 1000), "carIndex": carno, "type": "SPEED", "value": int(speed)} # prep speed message
    speedmessage = json.dumps(speeddata) # convert into JSON:
    client.publish("carStatus", speedmessage) # send mqtt message
    print(speedmessage)



myclient = pymongo.MongoClient('mongodb://localhost:27017/') # mongo connection
mydb = myclient['telemetry'] # mongo database name
mycol = mydb["cardata"] # mongo table name

redis_put_positions(positions) # redis initialise
redis_get_positions(oldpositions) # redis initialise
for startrace in range(cars_in_race):  # redis initialise
    carno = startrace # for each car
    redis_put_cardata(carno) # car number, timestamp, latitude, total distance, longitude

# client_name = os.system("hostname")  # to get the hostname
Connected = False   #global variable for the state of the connection
broker_address= "localhost" # mqtt broker details
client = mqttClient.Client("allanpythoncode")  # mqtt client - unique name / instance
client.on_connect= on_connect  # attach function to callback
client.on_message= on_message # attach function to callback
client.connect("localhost") # connect to mqtt broker
client.loop_start() # start the loop
while Connected != True: # Wait for connection
    time.sleep(0.1)
client.subscribe("carCoordinates")
try:
    while True:
        time.sleep(0.025)
except KeyboardInterrupt:
    print( "exiting")
    client.disconnect()
    client.loop_stop()
