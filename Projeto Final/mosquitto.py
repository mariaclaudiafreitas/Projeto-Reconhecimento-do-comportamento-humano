import paho.mqtt.client as mqtt

# Função chamada quando a conexão ao broker for bem-sucedida
def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker MQTT com código de resultado: " + str(rc))
    # Inscreve-se nos tópicos relacionados às emoções
    client.subscribe("emocao/#")  # O # permite subscrever a todos os tópicos que começam com "emocao/"

# Função chamada quando uma mensagem é recebida
def on_message(client, userdata, msg):
    emotion = msg.topic.split("/")[-1]  # Extrai a emoção do tópico (por exemplo, "emocao/feliz")
    print(f"Mensagem recebida - Emoção: {emotion}, Detalhes: {msg.payload.decode()}")

# Criar um cliente MQTT
client = mqtt.Client()

# Associar as funções de conexão e mensagem
client.on_connect = on_connect
client.on_message = on_message

# Conectar ao broker Mosquitto (localhost)
client.connect("localhost", 1883, 60)

# Iniciar o loop do cliente em segundo plano para processar mensagens recebidas
client.loop_start()

# Enviar uma mensagem de teste para validar a conexão e o recebimento
client.publish("emocao/teste", "Teste de mensagem MQTT para verificação de conexão")

# Manter o script ativo para que o cliente continue ouvindo e recebendo mensagens
try:
    input("Pressione Enter para sair...\n")
finally:
    client.loop_stop()  # Para o loop ao sair
    client.disconnect()  # Desconecta do broker
