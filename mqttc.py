# encoding: utf-8


import paho.mqtt.client as mqtt
import json
import os

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



def on_publish_tb(topic, payload, qos):
    print("pub:",topic,payload,qos)
    # Topic: v1 / gateway / connect
    # Message: {"device": "Device A"}
    client_tb.publish(topic, json.dumps({"device":payload}), qos)
    # client_tb.disconnect()


def on_connect(client, userdata, flags, rc):
    print("Connected with result code t2:"+str(rc))
    client.subscribe("kbeacon/publish/D03304000652")

def on_message(client, userdata, msg):
    print(msg.topic+" " + ":" + str(msg.payload,encoding = "utf-8"))
    msg_data = str(msg.payload,encoding = "utf-8")
    d = eval(msg_data)

    esl_gateway = d["gmac"]
    print("gmac:"+esl_gateway)
    print(len(d["obj"]))

    for i in range(len(d["obj"])):
        if d["obj"][i]["dmac"] != "" and d["obj"][i]["dmac"] not in esl_devices:
            print(d["obj"][i]["dmac"])
            esl_devices.append(d["obj"][i]["dmac"])

            # cmd = "mosquitto_pub -h 192.168.2.176 -p 1883 -t \"v1/gateway/connect\"  -m '{\"device\":\""+ d["obj"][i]["dmac"] +"\"}' -u \"H3wn8ScdYAiFPurZVsv4\""
            # os.system(cmd)
            on_publish_tb("v1/gateway/connect",d["obj"][i]["dmac"],0)


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

while True:
    device = input("device: ")
    # device = 'test\" -u \"H3wn8ScdYAiFPurZVsv4'
    on_publish_tb('v1/gateway/connect',device,0)
    if device == 'break':
        break
    pass


client.loop_stop()
client.disconnect()