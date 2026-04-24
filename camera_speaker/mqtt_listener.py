"""MQTT listener — subscribes to speak/camera1 and triggers TTS."""

import paho.mqtt.client as mqtt

from camera_speaker.api import say

BROKER = "mqtt.retallack.org.uk"
TOPIC = "speak/camera1"


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to {BROKER}, subscribing to {TOPIC}")
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    text = msg.payload.decode("utf-8", errors="replace").strip()
    if not text:
        return
    print(f"Received: {text}")
    try:
        say(text, host="camera1")
    except Exception as e:
        print(f"Error: {e}")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, 1883, 60)
    print(f"Listening on {BROKER} topic {TOPIC} ...")
    client.loop_forever()


if __name__ == "__main__":
    main()
