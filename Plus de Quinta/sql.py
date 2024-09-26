import paho.mqtt.client as mqtt
import sqlite3
import datetime

# Função que será chamada ao receber uma mensagem
def on_message(client, userdata, message):
    try:
        emotion = str(message.payload.decode("utf-8"))
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Conectar ao banco de dados SQLite usando o gerenciador de contexto `with`
        with sqlite3.connect('emotions.db') as conn:
            cursor = conn.cursor()

            # Criar a tabela se não existir
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emotions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    emotion TEXT NOT NULL
                )
            ''')

            # Inserir a emoção no banco de dados
            cursor.execute("INSERT INTO emotions (timestamp, emotion) VALUES (?, ?)", (timestamp, emotion))
            conn.commit()
        
        print(f"Emoção recebida e armazenada: {emotion} às {timestamp}")

    except Exception as e:
        print(f"Erro ao processar a mensagem: {e}")

# Configurações do MQTT
broker_address = "localhost"  # Substitua pelo endereço do seu broker
client = mqtt.Client("EmotionCollector")
client.on_message = on_message

try:
    # Conectar ao broker MQTT
    client.connect(broker_address)
    print(f"Conectado ao broker MQTT em {broker_address}")

    # Inscrever-se no tópico
    client.subscribe("emotion_topic")  # Substitua pelo tópico correto
    print("Inscrito no tópico 'emotion_topic'")

    # Iniciar o loop para ouvir as mensagens
    client.loop_forever()

except Exception as e:
    print(f"Erro ao conectar ao broker MQTT: {e}")
