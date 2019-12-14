#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paho.mqtt.subscribe as subscribe # add MQTT tools
import json # add json<>python object tools
from geopy.distance import geodesic # add gps tools
from datetime import datetime # add timestamp tools
import time # add time tools
import redis  # add redis tools
from cassandra import ConsistencyLevel # add cassandra HA tools
from cassandra.query import SimpleStatement # add cassandra HA tools
from cassandra.cluster import Cluster # add cassandra HA tools
from cassandra.policies import DCAwareRoundRobinPolicy # add cassandra HA tools
cars_in_race = 6 # reduce the hardcoding, revisit positions list
import pymongo
import urllib.parse
origin = (52.06813447551777,  -1.023626530253432431) # random point on track - eventually startline
topics = ['#'] # set topic to listen to
now = datetime.now() # get current timestamp
racedata = [] # setup empty list, current race data in memory, each car has it's own list within
positions = [0,1,2,3,4,5] # setup list, current race positions data in memory
oldpositions = [0,0,0,0,0,0]  # setup empty list, to be used to detect overtakes
# racedata car lists - last timestamp, last gps, total distance, position
for startrace in range(cars_in_race):
  racedataelement = [startrace,datetime.timestamp(now), origin, 0, (startrace + 1)]
  racedata.insert(startrace, racedataelement)
print(racedata)
r = redis.Redis() # initialise the redis cache
# r.mset({"position0": positions[0], "position1": positions[1], "position2": positions[2], "position3": positions[3], "position4": positions[4], "position5": positions[5],})
# print(r.get("racedata"), "racedata from redis cache")
# print(r.get("racedata"), "positions from redis cache")
r.mset({"Croatia": "Zagreb", "Bahamas": "Nassau"})
print(r.get("Bahamas"))


# cluster = Cluster()
# session = cluster.connect()
username = urllib.parse.quote_plus('user')
password = urllib.parse.quote_plus('password')
myclient = pymongo.MongoClient('mongodb://localhost:27017/')
mydb = myclient['telemetry']
mycol = mydb["cardata"]



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
      fname[2] = (float(r.get("lat0")), float(r.get("long0")))
      fname[3] = float(r.get("totaldistance0"))
  if carno == 1:
      fname[0] = 1
      fname[1] = float(r.get("timestamp1"))
      fname[2] = (float(r.get("lat1")), float(r.get("long1")))
      fname[3] = float(r.get("totaldistance1"))
  if carno == 2:
      fname[0] = 2
      fname[1] = float(r.get("timestamp2"))
      fname[2] = (float(r.get("lat2")), float(r.get("long2")))
      fname[3] = float(r.get("totaldistance2"))
  if carno == 3:
      fname[0] = 3
      fname[1] = float(r.get("timestamp3"))
      fname[2] = (float(r.get("lat3")), float(r.get("long3")))
      fname[3] = float(r.get("totaldistance3"))
  if carno == 4:
      fname[0] = 4
      fname[1] = float(r.get("timestamp4"))
      fname[2] = (float(r.get("lat4")), float(r.get("long4")))
      fname[3] = float(r.get("totaldistance4"))
  if carno == 5:
      fname[0] = 5
      fname[1] = float(r.get("timestamp5"))
      fname[2] = (float(r.get("lat5")), float(r.get("long5")))
      fname[3] = float(r.get("totaldistance5"))

print("old positions", oldpositions)

redis_put_positions(positions)
redis_get_positions(oldpositions)

print("old positions", oldpositions)


print("old positions", oldpositions)

m = subscribe.simple(topics, hostname="localhost", retained=False, msg_count=20) # read 20 messages
for a in m: # run this code for each message
    print(a.payload)
    cardata = json.loads(a.payload) # convert current message from JSON
    mydict = { "carIndex": (cardata["carIndex"]), "latitude": (cardata["location"].get("lat")), "longitude": (cardata["location"].get("long")), "timestamp": (cardata["timestamp"])}
    x = mycol.insert_one(mydict)
    carno = int(cardata["carIndex"]) # extract car number from message
    newtimestamp = (cardata["timestamp"]/1000.0) # extract timestamp from message and adjust value for processing
    tracklat = float(cardata["location"].get("lat")) # extract currrent gps
    tracklong = float(float(cardata["location"].get("long"))) # extract currrent gps
    trackgps = (float(cardata["location"].get("lat")),float(cardata["location"].get("long"))) # extract currrent gps
    oldinfo = racedata[carno] # obtain last saved data for current car
    oldgps = oldinfo[2] # last known GPS position for current car
    olddistance = oldinfo[3] # last known total distance for current car
    oldtimestamp = oldinfo[1] # last known timestamp for current car
    olddate = datetime.fromtimestamp(oldtimestamp) # calculate date of last timestamp
    newdate = datetime.fromtimestamp(newtimestamp) # calculate date of last timestamp
    tripdistance = geodesic(oldgps, trackgps).kilometers # calculate delta distance
    timedifference = newdate - olddate  # calculate time delta
    totaldistance = olddistance + tripdistance # calculate new total race distance
    timediffmicro = timedifference.microseconds # convert time delta to micro s
    speed = (tripdistance * 1000000 * 3600 / timediffmicro) # calculate current speed
    newinfo = [carno,newtimestamp,trackgps,totaldistance] # prep current values for saving
    redis_put_cardata(carno)
    if carno == 0:
        # print(a.payload)
        # print(carno,tripdistance,totaldistance, timedifference, timediffmicro, speed,"carno, tripdist, totaldist, timediff, timediff(us), speed")
        # print(oldinfo, newinfo, "old, new")
        # print(racedata)
        racedistance = [racedata[0][3], racedata[1][3], racedata[2][3], racedata[3][3], racedata[4][3], racedata[5][3]] # use cars_in_race, total distance driven
        leaderdistance = sorted(racedistance, key=float, reverse=True) # order total distance
        # print(racedistance,leaderdistance, "racedistance unsorted - sorted leader distance")
        for raceorder in range(cars_in_race): # revisit in case more efficient mthond
            for distances in range(cars_in_race):
                if racedistance[raceorder] == leaderdistance[distances] and leaderdistance != 0:
                    positions[distances] = raceorder # calculate race order on total distance
        # print(positions, oldpositions, "positions - old positions")
        for positionorder in range(cars_in_race):
            positiondata = {"timestamp": int(newtimestamp * 1000), "carIndex": positionorder, "type": "POSITION", "value": (positions[positionorder] + 1)} # prep position message
            positionmessage = json.dumps(positiondata) # convert into JSON:
            print(positionmessage)
        if positions != oldpositions:
            eventdata = {"timestamp": int(newtimestamp * 1000), "text": "overtake detected"} # prep event message
            eventmessage = json.dumps(eventdata) # convert into JSON:
            print(eventmessage)
            oldpositions = positions
    racedata[carno] = newinfo # save updated data for current car
    speeddata = {"timestamp": int(newtimestamp * 1000), "carIndex": carno, "type": "SPEED", "value": int(speed)} # prep speed message
    speedmessage = json.dumps(speeddata) # convert into JSON:
    # print(speedmessage) # send speed message
print(racedata)
rediscar=[0,0,0,0]
carno=0
redis_get_car(rediscar)
print(rediscar, "fetched from redis ", carno)
carno=1
redis_get_car(rediscar)
print(rediscar, "fetched from redis ", carno)
carno=2
redis_get_car(rediscar)
print(rediscar, "fetched from redis ", carno)
carno=3
redis_get_car(rediscar)
print(rediscar, "fetched from redis ", carno)
carno=4
redis_get_car(rediscar)
print(rediscar, "fetched from redis ", carno)
carno=5
redis_get_car(rediscar)
print(rediscar, "fetched from redis ", carno)

