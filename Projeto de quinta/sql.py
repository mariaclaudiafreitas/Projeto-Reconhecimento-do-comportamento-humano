import paho.mqtt.client as mqtt
import sqlite3
import datetime

# Função que será chamada ao receber uma mensagem
def on_message(client, userdata, message):
    emotion = str(message.payload.decode("utf-8"))
    timestamp = datetime.datetime.now()

    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect('emotions.db')
    cursor = conn.cursor()

    # Inserir a emoção no banco de dados
    cursor.execute("INSERT INTO emotions (timestamp, emotion) VALUES (?, ?)", (timestamp, emotion))
    conn.commit()
    conn.close()

# Configurações do MQTT
broker_address = "localhost"  # Substitua pelo endereço do seu broker
client = mqtt.Client("EmotionCollector")
client.on_message = on_message

client.connect(broker_address)
client.subscribe("emotion_topic")  # Substitua pelo tópico correto

client.loop_forever()
