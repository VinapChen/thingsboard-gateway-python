# encoding: utf-8


import paho.mqtt.client as mqtt
import json
import os
import time

esl_gateway = ""
esl_devices = []


user_gateway = 'H3wn8ScdYAiFPurZVsv4'
server_tb = '192.168.2.176'
port_tb = 1883

server = 'localhost'
port = 1883

def on_connect_tb(client_tb, userdata, flags, rc):
    print("Connected with result code t1:"+str(rc))

def on_message_tb(client_tb, userdata, msg):
    print(msg.topic+" " + ":" + str(msg.payload,encoding = "utf-8"))
    client_tb.subscribe([("v1/gateway/rpc", 0), ("v1/gateway/attributes", 0),("v1/gateway/attributes/response",0)])


def on_publish_tb(topic, payload, qos):
    print("pub:",topic,payload,qos)
    client_tb.publish(topic, payload, qos)
    # client_tb.disconnect()


def on_connect(client, userdata, flags, rc):
    print("Connected with result code t2:"+str(rc))
    client.subscribe("kbeacon/publish/D03304000652")

message = {}
telemetry_message = {}
def on_message(client, userdata, msg):
    global message
    global telemetry_message

    message = {}
    telemetry_message = {}

    print(msg.topic+" " + ":" + str(msg.payload,encoding = "utf-8"))
    msg_data = str(msg.payload,encoding = "utf-8")
    d = eval(msg_data)

    esl_gateway = d["gmac"]
    print("gmac:"+esl_gateway)
    print(len(d["obj"]))

    for i in range(len(d["obj"])):
        # add new device
        # Topic: v1 / gateway / connect
        # Message: {"device": "Device A"}
        if d["obj"][i]["dmac"] != "" and d["obj"][i]["dmac"] not in esl_devices:
            print(d["obj"][i]["dmac"])
            esl_devices.append(d["obj"][i]["dmac"])
            on_publish_tb("v1/gateway/connect",json.dumps({"device":d["obj"][i]["dmac"]}),0)

        #    pub attributes data
        # Topic: v1 / gateway / attributes
        # Message: {"Device A": {"attribute1": "value1", "attribute2": 42},
        #           "Device B": {"attribute1": "value1", "attribute2": 42}}
        batteryV = float(int(d["obj"][i]["data1"][30:34],16)/1000)   #BYTE 15,16
        temperature = float(int(d["obj"][i]["data1"][34:36],16)) + float(int(d["obj"][i]["data1"][36:38],16)/100)   #BYTE 17,18
        data = {
            d["obj"][i]["dmac"]:{"RSSI":d["obj"][i]["rssi"],
                                 "TYPE":d["obj"][i]["data1"][22:24],    #BYTE 11
                                 "FWVersion":d["obj"][i]["data1"][24:26],   #BYTE 12
                                 "Ability":d["obj"][i]["data1"][26:28],     #BYTE 13,    14 reserve
                                 "BattVolt":batteryV,
                                 "Temperature":temperature,
                                 "PictureID":d["obj"][i]["data1"][38:46],    #BYTE 19, 20, 21, 22
                                 }
        }
        message = dict(message, **data)

        #     Topic: v1/gateway/telemetry
        telemetry_data = {
            d["obj"][i]["dmac"]: [
                {
                    "ts": int(round(time.time() * 1000)),
                    "values": {
                        "temperature": temperature,
                        "batteryV": batteryV
                    }
                }
            ]
        }
        telemetry_message = dict(telemetry_message, **telemetry_data)

    on_publish_tb("v1/gateway/attributes", json.dumps(message), 0)
    on_publish_tb("v1/gateway/telemetry",json.dumps(telemetry_message),0)

    print(esl_devices)

client = mqtt.Client("client_for_esl")

client.on_connect = on_connect
client.on_message = on_message
client.connect(server, port)

client_tb = mqtt.Client('client_to_tb')
client_tb.username_pw_set(user_gateway)
client_tb.on_connect = on_connect_tb
client_tb.on_message = on_message_tb

client_tb.connect(server_tb, port_tb)

# client.loop_start()
# client_tb.loop_forever()

client.loop_start()
client_tb.loop_start()

# device = 'test\" -u \"H3wn8ScdYAiFPurZVsv4'
# on_publish_tb('v1/gateway/connect', device, 0)

# request attributes
# Topic: v1/gateway/attributes/request
# Message = {"id":"1112", "device": "2735000A33DD", "client": "true", "key": "BattVolt"}
# on_publish_tb('v1/gateway/attributes/request', json.dumps(Message), 0)

while True:
    device = input("device: ")
    # device = 'test\" -u \"H3wn8ScdYAiFPurZVsv4'
    on_publish_tb('v1/gateway/disconnect',device,0)
    if device == 'break':
        break
    pass


client.loop_stop()
client.disconnect()