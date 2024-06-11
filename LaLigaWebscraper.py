import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

s = Service(ChromeDriverManager().install())
opc = Options()
opc.add_argument("fullscreen")

navegador = webdriver.Chrome(service=s, options=opc)
navegador.get("https://www.espn.com.mx/futbol/posiciones/_/liga/esp.1/temporada/2023")

cmbTemporada = navegador.find_element(By.CSS_SELECTOR, ".dropdown__select[aria-label='Clasificaciones de temporada']")
temporada_options = cmbTemporada.find_elements(By.TAG_NAME, "option")

datos = {
    "Temporada": [],
    "Equipo": [],
    "JJ": [],
    "JG": [],
    "JE": [],
    "JP": [],
    "GF": [],
    "GC": [],
    "DF": [],
    "PTS": []
}

for temporada in temporada_options[0:]:
    temporada_nombre = temporada.text
    temporada.click()
    time.sleep(2)

    soup = BeautifulSoup(navegador.page_source, "html.parser")
    tabla_equipos = soup.find("table", attrs={"class": "Table"})
    filas_equipos = tabla_equipos.find_all("tr")

    for fila in filas_equipos[1:]:
        celdas = fila.find_all(["td", "th"])
        equipo_celda = fila.find("div", class_="team-link").find("span", class_="hide-mobile").find("a")
        try:
            datos["Temporada"].append(temporada_nombre)
            nombre_equipo = equipo_celda.text.strip()
            datos["Equipo"].append(nombre_equipo)
        except AttributeError:
            print(f"No se pudo encontrar el nombre del equipo para la temporada {temporada_nombre}")

    tabla_datos = soup.find("table", attrs={"class": "Table Table--align-right"})
    filas_datos = tabla_datos.find_all("tr")

    for fila in filas_datos[1:]:
        celdas = fila.find_all("td")

        try:
            jj = celdas[0].find("span", class_="stat-cell").text.strip()
            datos["JJ"].append(jj)
            jg = celdas[1].find("span", class_="stat-cell").text.strip()
            datos["JG"].append(jg)
            je = celdas[2].find("span", class_="stat-cell").text.strip()
            datos["JE"].append(je)
            jp = celdas[3].find("span", class_="stat-cell").text.strip()
            datos["JP"].append(jp)
            gf = celdas[4].find("span", class_="stat-cell").text.strip()
            datos["GF"].append(gf)
            gc = celdas[5].find("span", class_="stat-cell").text.strip()
            datos["GC"].append(gc)
            dif = celdas[6].find("span", class_="stat-cell").text.strip()
            datos["DF"].append(dif)
            pts = celdas[7].find("span", class_="stat-cell").text.strip()
            datos["PTS"].append(pts)
        except AttributeError:
            print(f"Error")

navegador.quit()

data_df = pd.DataFrame(datos)
data_df.to_csv("laliga.csv")
