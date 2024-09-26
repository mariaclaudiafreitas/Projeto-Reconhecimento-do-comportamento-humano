import pandas as pd
import sqlite3

# Conectar ao banco de dados SQLite
conn = sqlite3.connect('emotions.db')

# Carregar os dados em um DataFrame do Pandas
df = pd.read_sql_query("SELECT * FROM emotions", conn)

# Exportar para CSV
df.to_csv('emotions.csv', index=False)

conn.close()
