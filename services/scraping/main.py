from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/scrape/{empresa}")
async def scrape_data(empresa: str):
    if empresa == "afp_habitat":
        url = "https://www.afphabitat.cl/nuestra-empresa/estatutos-y-estados-financieros/"
        # Simulación de scraping de AFP Habitat (modifica según tu lógica)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        # Procesar y extraer datos aquí según la estructura HTML específica
        data = {"empresa": empresa, "data": "Datos scrapeados de ejemplo"}
        return data
    elif empresa == "zofri":
        url = "https://www.zofri.cl/es-cl/Financiera/Paginas/EstadosFinancieros.aspx#/collapse1"
        # Simulación de scraping de Zofri (modifica según tu lógica)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        # Procesar y extraer datos aquí
        data = {"empresa": empresa, "data": "Datos scrapeados de ejemplo"}
        return data
    else:
        return {"error": "Empresa no soportada"}
