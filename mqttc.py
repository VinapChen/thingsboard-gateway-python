# encoding: utf-8


import paho.mqtt.client as mqtt
import json
import os

esl_gateway = ""
esl_devices = []

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("kbeacon/publish/D03304000652")


def on_message(client, userdata, msg):
    print(msg.topic+" " + ":" + str(msg.payload,encoding = "utf-8"))
    msg_data = str(msg.payload,encoding = "utf-8")
    d = eval(msg_data)
    print(type(d))
    # j = json.dumps(d)
    #
    # msg_json = json.loads(j)
    # print(msg_json)
    esl_gateway = d["gmac"]
    print(esl_gateway)
    print(len(d["obj"]))

    for i in range(len(d["obj"])):
        if d["obj"][i]["dmac"] != "" and d["obj"][i]["dmac"] not in esl_devices:
            print(d["obj"][i]["dmac"])
            esl_devices.append(d["obj"][i]["dmac"])

            cmd = "mosquitto_pub -h 192.168.2.176 -p 1883 -t \"v1/gateway/connect\"  -m '{\"device\":\""+ d["obj"][i]["dmac"] +"\"}' -u \"H3wn8ScdYAiFPurZVsv4\""
            os.system(cmd)


    print(esl_devices)
    # print(devices_data)
    # print(devices_data1)
    # obj = eval(d["obj"])
    # print(type(obj),obj["dmac"])


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883)
client.loop_forever()