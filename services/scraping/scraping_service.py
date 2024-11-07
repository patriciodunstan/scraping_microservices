import os
import json
from fastapi import FastAPI, HTTPException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = FastAPI()

def cargar_configuracion(empresa):
    """Carga la configuración JSON de una empresa desde el archivo en la carpeta configurations."""
    try:
        # Cambia la ruta a la subcarpeta dentro de services/scraping/configurations
        config_path = os.path.join(os.path.dirname(__file__), "configurations", f"{empresa}.json")
        with open(config_path, "r") as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Empresa no soportada")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error en la configuración de la empresa")


def iniciar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Ejecutar en modo sin cabeza
    options.add_argument("--no-sandbox")  # Evitar problemas de sandboxing en Docker
    options.add_argument("--disable-dev-shm-usage")  # Solucionar problemas de memoria en contenedores
    options.add_argument("--disable-gpu")  # Deshabilitar GPU (opcional)
    options.add_argument("--remote-debugging-port=9222")  # Habilitar puerto para depuración (opcional)
    driver = webdriver.Chrome(options=options)
    return driver

def realizar_acciones(driver, acciones):
    try:
        # Selecciona el mes si está configurado
        if "select_mes" in acciones:
            select_mes = acciones["select_mes"]
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, select_mes["selector"]))
            ).send_keys(select_mes["value"])

        # Selecciona el año si está configurado
        if "select_año" in acciones:
            select_año = acciones["select_año"]
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, select_año["selector"]))
            ).send_keys(select_año["value"])

        # Haz clic en el botón de descarga si está configurado
        if "boton_descarga" in acciones:
            boton_descarga = acciones["boton_descarga"]
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, boton_descarga["selector"]))
            ).click()
    except Exception as e:
        print(f"Error al realizar acciones previas: {e}")


def scrapear_estado_financiero(driver, config):
    driver.get(config['url'])

    # Realizar acciones previas (si existen) como seleccionar mes/año o hacer clic en botones
    if "acciones" in config:
        realizar_acciones(driver, config["acciones"])

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, config['elemento_principal']))
    )
    estados_financieros = []
    elementos = driver.find_elements(By.CSS_SELECTOR, config['elemento_filas'])
    print(f"Elementos encontrados: {len(elementos)}")  # Debug

    for elemento in elementos:
        try:
            nombre = elemento.find_element(By.CSS_SELECTOR, config['nombre']).text
            periodo = elemento.find_element(By.CSS_SELECTOR, config['periodo']).text
            fecha = elemento.find_element(By.CSS_SELECTOR, config['fecha']).text
            print(f"Datos extraídos: Nombre: {nombre}, Periodo: {periodo}, Fecha: {fecha}")  # Debug
            estado = {
                "nombre": nombre,
                "periodo": periodo,
                "fecha": fecha,
            }
            estados_financieros.append(estado)
        except Exception as e:
            print(f"Error al obtener datos: {e}")
    
    return estados_financieros


@app.get("/scrape/{empresa}")
async def scrape_empresa(empresa: str, mes: str = None, año: str = None):

    config = cargar_configuracion[empresa]

    # Modificar valores en config según los parámetros recibidos
    if "acciones" in config:
        if mes:
            config["acciones"]["select_mes"]["value"] = mes
        if año:
            config["acciones"]["select_año"]["value"] = año

    driver = iniciar_driver()
    try:
        data = scrapear_estado_financiero(driver, config)
        return {"empresa": empresa, "data": data}
    finally:
        driver.quit()
