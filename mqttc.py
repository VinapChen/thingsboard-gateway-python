# encoding: utf-8


import paho.mqtt.client as mqtt
import json
import os
import time
import requests
import re

esl_gateway = ""
esl_devices = []
esl_type = []

rpc_result = 'true'


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
    global rpc_result
    temp_id = 99
    params_len = 0
    picture_id = 0
    rpc_result = 'true'

    print("sub:",msg.topic+" " + ":" + str(msg.payload,encoding = "utf-8"))
    payload = str(msg.payload, encoding="utf-8")
    payload_json = eval(payload)
    if msg.topic == "v1/gateway/rpc":
        print("json paylosd rpc id:",payload_json['data']['id'])
        # params = eval(payload_json['data']['params'])
        # print("json paylosd rpc params:",params['id'],params['type'])
        device_name = payload_json['device']
        device_mac = device_name_to_mac(device_name)
        index = esl_devices.index(device_mac)
        size = esl_type[index]
        print(device_mac,index,size)

        method = payload_json['data']['method'].split(',')
        if len(method)>2:
            rpc_result = "Template id or picture id error"
        elif len(method) == 2:
            try:
                picture_id = int(method[1])
            except Exception as e:
                print("picture_id error reason:",e)
                if rpc_result == 'true':
                    rpc_result = "Picture id error"

        try:
            temp_id = int(method[0])
        except Exception as e:
            print("temp_id error reason:",e)
            if rpc_result == 'true':
                rpc_result = "Template id error"
        try:
            params = payload_json['data']['params']
            temp_params = params.split(',')
            params_len = len(temp_params)
        except Exception as e:
            print("params error reason:",e)
            if rpc_result == 'true':
                rpc_result = "Params error"

        # print(temp_id,temp_params,params_len)

        if temp_id == 0:
            if params_len != 6:
                if rpc_result == 'true':
                    rpc_result = "Params error"

            try:
                price = float(temp_params[4])
            except Exception as e :
                print("price error reason: ",e)
                if rpc_result == 'true':
                    rpc_result = 'price error'
            try:
                productNumber = int(temp_params[5])
            except Exception as e :
                print("productNumber error reason:",e)
                if rpc_result == 'true':
                    rpc_result = 'product number error'

            if rpc_result == 'true':
                data = {"data":{"title":temp_params[0],
                        "subTitle1":temp_params[1],
                        "subTitle2":temp_params[2],
                        "currency":temp_params[3],
                        "price":price,
                        "productNumber":str(productNumber)},"temp_id":temp_id,"size":size,"mac":device_mac,"picture_id":picture_id}

        elif temp_id == 1:
            if size not in [1,3]:
                if rpc_result == 'true':
                    rpc_result = 'Template id error'
            if params_len != 2:
                if rpc_result == 'true':
                    rpc_result = "Params error"

            if rpc_result == 'true':
                data = {"data":{"title":temp_params[0],
                        "subTitle":temp_params[1]},"temp_id":temp_id,"size":size,"mac":device_mac,"picture_id":picture_id}

        elif temp_id == 2:
            if size not in [1,3]:
                if rpc_result == 'true':
                    rpc_result = 'Template id error'
            elif size ==1 :
                if params_len != 1:
                    if rpc_result == 'true':
                        rpc_result = "Params error"
                if rpc_result == 'true':
                    data = {"data": {"title": temp_params[0]}, "temp_id": temp_id, "size": size, "mac": device_mac,"picture_id":picture_id}
            elif size ==3:
                if params_len != 3:
                    rpc_result = "Params error"
                if rpc_result == 'true':
                    data = {"data": {"title": temp_params[0],
                                     "subTitle": temp_params[1],
                                     "description":temp_params[2]}, "temp_id": temp_id, "size": size, "mac": device_mac,"picture_id":picture_id}

        elif temp_id == 3:
            if size not in [1]:
                if rpc_result == 'true':
                    rpc_result = 'Template id error'
            elif size == 1 :
                if params_len != 2:
                    if rpc_result == 'true':
                        rpc_result = "Params error"
                if rpc_result == 'true':
                    data = {"data": {"title": temp_params[0],
                                     "subTitle": temp_params[1]}, "temp_id": temp_id, "size": size, "mac": device_mac,"picture_id":picture_id}


        else:
            rpc_result = 'Template id error'

        if rpc_result == 'true':
            requrl = "http://0.0.0.0:8080/txt2json"
            r = requests.post(requrl, data=json.dumps(data))
            print(r.text)

            on_publish('kbeacon/subaction/D03304000652',r.text,0)


        response_rpc = {"device": payload_json['device'], "id": payload_json['data']['id'], "data": {"success":rpc_result}}
        on_publish_tb("v1/gateway/rpc",json.dumps(response_rpc),0)

    elif "v1/devices/me/rpc/request/" in msg.topic:
        on_publish_tb(msg.topic.replace('request', 'response'),json.dumps({"success": "true"}),0)

def on_publish_tb(topic, payload, qos):
    if topic == "v1/gateway/rpc" or "v1/devices/me/rpc/response/" in topic:
        print("pub:",topic,payload,qos)
    try:
        client_tb.publish(topic, payload, qos)
    except Exception as e:
        print("pub error:")
    # client_tb.disconnect()


def on_connect(client, userdata, flags, rc):
    print("Connected with result code t2:"+str(rc))
    client.subscribe("kbeacon/publish/D03304000652")

message = {}
telemetry_message = {}
def on_message(client, userdata, msg):
    global message
    global telemetry_message
    global esl_devices,esl_gateway,esl_type

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

        device_name = device_mac_to_name(d["obj"][i]["dmac"])
        if d["obj"][i]["dmac"] != "" and d["obj"][i]["dmac"] not in esl_devices:
            # print(d["obj"][i]["dmac"])
            esl_devices.append(d["obj"][i]["dmac"])
            esl_type.append(int(d["obj"][i]["data1"][29:30]))
            on_publish_tb("v1/gateway/connect",json.dumps({"device":device_name}),0)

        #    pub attributes data
        # Topic: v1 / gateway / attributes
        # Message: {"Device A": {"attribute1": "value1", "attribute2": 42},
        #           "Device B": {"attribute1": "value1", "attribute2": 42}}
        batteryV = float(int(d["obj"][i]["data1"][30:34],16)/1000)   #BYTE 15,16
        temperature = float(int(d["obj"][i]["data1"][34:36],16)) + float(int(d["obj"][i]["data1"][36:38],16)/100)   #BYTE 17,18
        data = {
            device_name:{"RSSI":d["obj"][i]["rssi"],
                                 "SensorType":d["obj"][i]["data1"][22:24],    #BYTE 11
                                 "FWVersion":d["obj"][i]["data1"][24:26],   #BYTE 12
                                 "Ability":d["obj"][i]["data1"][26:28],     #BYTE 13,    14 reserve
                                 "ESLType":d["obj"][i]["data1"][29:30],     #0x0:2.9inch white/black     0x1:2.9inch white/black/red    0x2:4.2inch white/black
                                                                            # 0x3:4.2inch white/black/red       0x4:2.1inch white/black         0x5: 2.1inch white/black/red
                                 "BattVolt":batteryV,
                                 "Temperature":temperature,
                                 "PictureID":int(d["obj"][i]["data1"][38:46],16),    #BYTE 19, 20, 21, 22 HEX to DEC
                                 }
        }
        message = dict(message, **data)

        #     Topic: v1/gateway/telemetry
        telemetry_data = {
            device_name: [
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
    # print(esl_type)

def on_publish(topic, payload, qos):
    global rpc_result
    print("pub:",topic,payload,qos)
    try :
        client.publish(topic, payload, qos)
    except Exception as e:
        print('reason:',e)
        rpc_result = 'The operation failed, please try again'

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


def device_mac_to_name(mac):
    t = re.findall(r'.{2}',mac)
    name = "Y-ESL "+t[5]+t[4]+t[3]+t[2]+t[1]+t[0]
    return name

def device_name_to_mac(name):
    n = name.split(" ")
    t = re.findall(r'.{2}',n[1])
    mac = t[5]+t[4]+t[3]+t[2]+t[1]+t[0]
    return mac


while True:
    device = input()
    # on_publish_tb('v1/gateway/disconnect',device,0)
    if device == 'exit':
        break
    pass


client.loop_stop()
client.disconnect()