# encoding: utf-8

import paho.mqtt.client as mqtt

HOST = "192.168.2.176"
PORT = 1883


def test():
    client = mqtt.Client()
    # client.username("H3wn8ScdYAiFPurZVsv4")
    client.connect(HOST, PORT, 60)
    client.publish("chat", "hello liefyuan", 0)  # 发布一个主题为'chat',内容为‘hello liefyuan’的信息
    client.disconnect()


if __name__ == '__main__':
    test()
