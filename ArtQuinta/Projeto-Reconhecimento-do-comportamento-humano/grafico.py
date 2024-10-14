import matplotlib.pyplot as plt

# Função para recuperar os dados e gerar um gráfico
def gerar_grafico_emocoes():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("SELECT emocao, SUM(quantidade) FROM emocoes GROUP BY emocao")
    resultados = cursor.fetchall()
    
    # Separar os dados para o gráfico
    emocoes = [row[0] for row in resultados]
    quantidades = [row[1] for row in resultados]
    
    # Gerar o gráfico
    plt.bar(emocoes, quantidades, color='skyblue')
    plt.xlabel('Emoções')
    plt.ylabel('Quantidade')
    plt.title('Quantidade de Emoções Detectadas')
    plt.show()
    
    cursor.close()
    conexao.close()

# Chame essa função para gerar o gráfico
gerar_grafico_emocoes()


