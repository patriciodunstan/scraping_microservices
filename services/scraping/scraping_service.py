from fastapi import FastAPI, HTTPException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

app = FastAPI()

# Configuraciones específicas para cada empresa
configuraciones = {
    "afp_habitat": {
        "url": "https://www.afphabitat.cl/nuestra-empresa/estatutos-y-estados-financieros/",
        "elemento_principal": "div.select",
        "elemento_filas": "div.financial-statements",
        "nombre": "h3",
        "periodo": "span.periodo",
        "fecha": "span.fecha",
    },
    "zofri": {
        "url": "https://www.zofri.cl/es-cl/Financiera/Paginas/EstadosFinancieros.aspx#/collapse1",
        "elemento_principal": "table",
        "elemento_filas": "table tr",
        "nombre": "td:nth-child(1)",
        "periodo": "td:nth-child(1)",
        "fecha": "td:nth-child(2)",
    }
}

def iniciar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    return driver

def scrapear_estado_financiero(driver, config):
    driver.get(config['url'])
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, config['elemento_principal']))
    )
    estados_financieros = []
    elementos = driver.find_elements(By.CSS_SELECTOR, config['elemento_filas'])
    for elemento in elementos:
        try:
            estado = {
                "nombre": elemento.find_element(By.CSS_SELECTOR, config['nombre']).text,
                "periodo": elemento.find_element(By.CSS_SELECTOR, config['periodo']).text,
                "fecha": elemento.find_element(By.CSS_SELECTOR, config['fecha']).text,
            }
            estados_financieros.append(estado)
        except Exception as e:
            print(f"Error al obtener datos: {e}")
    return estados_financieros

@app.get("/scrape/{empresa}")
async def scrape_empresa(empresa: str):
    if empresa not in configuraciones:
        raise HTTPException(status_code=404, detail="Empresa no soportada")
    config = configuraciones[empresa]
    driver = iniciar_driver()
    try:
        data = scrapear_estado_financiero(driver, config)
        return {"empresa": empresa, "data": data}
    finally:
        driver.quit()
