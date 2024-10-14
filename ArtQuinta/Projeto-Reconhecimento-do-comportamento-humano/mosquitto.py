import paho.mqtt.client as mqtt

# Função chamada quando a conexão for bem-sucedida
def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker MQTT com código de resultado: " + str(rc))
    client.subscribe("test/topic")

# Função chamada quando uma mensagem é recebida
def on_message(client, userdata, msg):
    print("Mensagem recebida no tópico " + msg.topic + ": " + str(msg.payload.decode()))

# Criar um cliente MQTT
client = mqtt.Client()

# Associar as funções de conexão e mensagem
client.on_connect = on_connect
client.on_message = on_message

# Conectar ao broker Mosquitto (localhost)
client.connect("localhost", 1883, 60)

# Iniciar o loop do cliente
client.loop_start()

# Publicar uma mensagem no tópico "test/topic"
client.publish("test/topic", "Olá MQTT!")

# Manter o script ativo para receber mensagens
input("Pressione Enter para sair...\n")
