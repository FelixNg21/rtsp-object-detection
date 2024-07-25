import paho.mqtt.client as mqtt

# MQTT broker (replace with your broker's IP address or hostname)
broker = "localhost"  # If running Mosquitto locally

# MQTT topic to subscribe to
topic = "test/topic"  # Modify to match the topic you want to subscribe to

# Callback function that is called when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribe to the topic when connected
    client.subscribe(topic)

# Callback function that is called when a message is received on the subscribed topic
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

# Create an MQTT client instance
client = mqtt.Client()

# Assign callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
client.connect(broker, 1883, 60)

# Loop to maintain network traffic flow and handle callbacks
client.loop_forever()
