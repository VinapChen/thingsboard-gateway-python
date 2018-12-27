# encoding: utf-8


import paho.mqtt.client as mqtt
import json
import os
import time
import requests

esl_gateway = ""
esl_devices = []


user_gateway = 'H3wn8ScdYAiFPurZVsv4'
server_tb = '192.168.2.176'
port_tb = 1883

server = 'localhost'
port = 1883

def on_connect_tb(client_tb, userdata, flags, rc):
    print("Connected with result code t1:"+str(rc))
    client_tb.subscribe([("v1/gateway/rpc", 0),
                         ("v1/gateway/attributes", 0),
                         ("v1/gateway/attributes/response",0),
                         ("v1/devices/me/rpc/request/+",0)])

def on_message_tb(client_tb, userdata, msg):
    print("sub:",msg.topic+" " + ":" + str(msg.payload,encoding = "utf-8"))
    payload = str(msg.payload, encoding="utf-8")
    payload_json = eval(payload)
    if msg.topic == "v1/gateway/rpc":
        print("json paylosd rpc id:",payload_json['data']['id'])
        # params = eval(payload_json['data']['params'])
        # print("json paylosd rpc params:",params['id'],params['type'])
        device_mac = payload_json['device']
        title = payload_json['data']['method']
        subtitle1 = payload_json['data']['params']
        print(device_mac,title,subtitle1)

        data = {"data":{"title":title,
                "subTitle1":subtitle1,
                "subTitle2":"深圳南山",
                "currency":"¥",
                "price":'12.255',
                "productNumber":'6925785604585'},"temp_id":0,"size":0,"mac":device_mac}
        requrl = "http://0.0.0.0:8080/txt2json"
        r = requests.post(requrl, data=json.dumps(data))
        print(r.text)

        on_publish('kbeacon/subaction/D03304000652',r.text,0)


        response_rpc = {"device": payload_json['device'], "id": payload_json['data']['id'], "data": {"success": "true"}}
        on_publish_tb("v1/gateway/rpc",json.dumps(response_rpc),0)

    elif "v1/devices/me/rpc/request/" in msg.topic:
        on_publish_tb(msg.topic.replace('request', 'response'),json.dumps({"success": "true"}),0)

def on_publish_tb(topic, payload, qos):
    if topic == "v1/gateway/rpc" or "v1/devices/me/rpc/response/" in topic:
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
    global esl_devices,esl_gateway

    message = {}
    telemetry_message = {}

    # print(msg.topic+" " + ":" + str(msg.payload,encoding = "utf-8"))
    msg_data = str(msg.payload,encoding = "utf-8")
    d = eval(msg_data)

    esl_gateway = d["gmac"]
    # print("gmac:"+esl_gateway)
    # print(len(d["obj"]))

    for i in range(len(d["obj"])):
        # add new device
        # Topic: v1 / gateway / connect
        # Message: {"device": "Device A"}
        if d["obj"][i]["dmac"] != "" and d["obj"][i]["dmac"] not in esl_devices:
            # print(d["obj"][i]["dmac"])
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
                                 "SensorType":d["obj"][i]["data1"][22:24],    #BYTE 11
                                 "FWVersion":d["obj"][i]["data1"][24:26],   #BYTE 12
                                 "Ability":d["obj"][i]["data1"][26:28],     #BYTE 13,    14 reserve
                                 "ESLType":d["obj"][i]["data1"][29:30],     #0x0:2.9inch white/black     0x1:2.9inch white/black/red    0x2:4.2inch white/black
                                                                            # 0x3:4.2inch white/black/red       0x4:2.1inch white/black         0x5: 2.1inch white/black/red
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

    # print(esl_devices)

def on_publish(topic, payload, qos):
    print("pub:",topic,payload,qos)
    try :
        client.publish(topic, payload, qos)
    except Exception as e:
        print('reason:',e)

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


while True:
    device = input()
    # on_publish_tb('v1/gateway/disconnect',device,0)
    if device == 'exit':
        break
    pass


client.loop_stop()
client.disconnect()