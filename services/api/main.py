from fastapi import FastAPI
import psycopg2
import os

app = FastAPI()

def get_db_connection():
    conn = psycopg2.connect(
        dbname="scraping",
        user="user",
        password="pass",
        host="localhost"
    )
    return conn

@app.get("/financial_data/{company}")
async def get_financial_data(company: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM financial_data WHERE company = %s", (company,))
    data = cursor.fetchall()
    conn.close()
    return {"data": data}
