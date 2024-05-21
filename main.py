import os
from dotenv import load_dotenv
import psycopg2
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def conectar_db():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    return conn

def obter_dados_acoes(pergunta):
    conn = conectar_db()
    cur = conn.cursor()
    query = f"""
    SELECT s.ticker, s.name, sp.date, sp.open, sp.high, sp.low, sp.close, sp.volume
    FROM stocks s
    JOIN stock_prices sp ON s.id = sp.stock_id
    WHERE s.name ILIKE %s OR s.ticker ILIKE %s;
    """
    cur.execute(query, (f"%{pergunta}%", f"%{pergunta}%"))
    resultados = cur.fetchall()
    cur.close()
    conn.close()
    return resultados

llm = ChatOpenAI(model_name="gpt-3.5-turbo")

def responder_pergunta(pergunta):
    dados_acoes = obter_dados_acoes(pergunta)
    if dados_acoes:
        resposta = f"Dados encontrados para '{pergunta}':\n"
        for dado in dados_acoes:
            resposta += f"Ticker: {dado[0]}, Nome: {dado[1]}, Data: {dado[2]}, Abertura: {dado[3]}, Máxima: {dado[4]}, Mínima: {dado[5]}, Fechamento: {dado[6]}, Volume: {dado[7]}\n"
    else:
        resposta = f"Nenhum dado encontrado para '{pergunta}'."
    return resposta

def main():
    pergunta = input("Sobre qual ação você deseja saber informações? ")
    resposta = responder_pergunta(pergunta)
    print(resposta)

if __name__ == "__main__":
    main()