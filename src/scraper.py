import csv
import re
import time
import sys
import logging
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime
from itertools import cycle
import threading

# ==================== CONFIGURACIÓN ====================
BASE_URL = "https://www.gelida.cat"
LISTADO_URL = urljoin(BASE_URL, "/el-municipi/empreses-i-comercos")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
OUTPUT_CSV = Path("data/directorio_gelida.csv")
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Configurar logging: solo guarda en archivo, no en consola
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE, encoding='utf-8')]
)

# ==================== SPINNER ====================
class Spinner:
    def __init__(self):
        self.spinner = cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.running = False
        self.thread = None
        self.message = ""

    def start(self, msg):
        self.message = msg
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()

    def _spin(self):
        while self.running:
            sys.stdout.write(f"\r{next(self.spinner)} {self.message} ")
            sys.stdout.flush()
            time.sleep(0.1)

    def stop(self, final_message=None):
        self.running = False
        if self.thread:
            self.thread.join()
        if final_message:
            sys.stdout.write(f"\r✅ {final_message}\n")
        else:
            sys.stdout.write("\r" + " " * (len(self.message) + 4) + "\r")
        sys.stdout.flush()

# ==================== EXTRACCIÓN DE DATOS ====================
def extraer_datos_detalle(url):
    """Extrae teléfono, dirección y email desde la página de detalle."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logging.error(f"Error accediendo a {url}: {e}")
        return "", "", ""

    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # ---- DIRECCIÓN (prioridad a relatedLocation) ----
    direccion = ""
    related_div = soup.find('div', class_=re.compile(r'relatedLocation', re.I))
    if related_div:
        for child in related_div.contents:
            if isinstance(child, str) and child.strip():
                linea = child.strip()
                if "08790" in linea:
                    direccion = re.sub(r'\s+', ' ', linea).strip()
                    break
        if not direccion:
            texto_div = related_div.get_text()
            match = re.search(r'([^<>\n]*08790[^<>\n]*)', texto_div)
            if match:
                direccion = re.sub(r'\s+', ' ', match.group(1)).strip()
    
    if not direccion:
        for clase in ['adreca', 'direccion', 'address', 'location']:
            elem = soup.find(['div', 'p', 'span'], class_=re.compile(clase, re.I))
            if elem:
                texto = elem.get_text(strip=True)
                if "08790" in texto and len(texto) < 200:
                    direccion = re.sub(r'\s+', ' ', texto)
                    break

    # ---- TELÉFONO ----
    telefono = ""
    tel_link = soup.find('a', href=lambda h: h and h.startswith('tel:'))
    if tel_link:
        num = tel_link['href'].replace('tel:', '').strip()
        if num and num != "937790058":
            telefono = num
    if not telefono:
        texto = soup.get_text()
        match = re.search(r'Tel[eè]fon:\s*(\d{9})', texto)
        if match:
            telefono = match.group(1)

    # ---- EMAIL ----
    email = ""
    mail_link = soup.find('a', href=lambda h: h and h.startswith('mailto:'))
    if mail_link:
        email = mail_link.get_text(strip=True) or mail_link['href'].replace('mailto:', '')
    if not email:
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', soup.get_text())
        if emails:
            email = emails[0]

    return telefono, direccion, email

# ==================== MAIN ====================
def main():
    print("🚀 Iniciando extracción (paginación + páginas de detalle)")
    print(f"📝 Los detalles de cada empresa se guardan en: {LOG_FILE}\n")

    spinner = Spinner()
    todos_registros = []
    pagina = 1

    while True:
        url_pagina = LISTADO_URL if pagina == 1 else f"{LISTADO_URL}?pag={pagina}"
        spinner.start(f"Escaneando página {pagina}...")
        
        try:
            resp = requests.get(url_pagina, headers=HEADERS, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            spinner.stop(f"❌ Error en página {pagina}: {e}")
            break
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        fichas = soup.find_all('li', class_='article-item')
        spinner.stop(f"Página {pagina} completada: {len(fichas)} empresas encontradas")
        
        if not fichas:
            break
        
        # Procesar cada empresa de la página
        for idx, ficha in enumerate(fichas, start=1):
            # Nombre
            nombre_elem = ficha.find('p', class_='subtitle') or ficha.find('a', class_='subtitle')
            if not nombre_elem:
                continue
            nombre_completo = nombre_elem.get_text(strip=True)
            partes = nombre_completo.split()
            nombre = partes[0]
            apellido = " ".join(partes[1:]) if len(partes) > 1 else ""
            
            # Email desde listado
            email_listado = ""
            mail_link = ficha.find('a', href=lambda h: h and h.startswith('mailto:'))
            if mail_link:
                email_listado = mail_link.get_text(strip=True) or mail_link['href'].replace('mailto:', '')
            
            # URL detalle
            enlace = ficha.find('a', href=True)
            url_detalle = urljoin(BASE_URL, enlace['href']) if enlace else None
            
            if url_detalle:
                # Mostrar spinner mientras se escanea la empresa
                spinner.start(f"Escaneando {nombre_completo[:30]}...")
                telefono, direccion, email_detalle = extraer_datos_detalle(url_detalle)
                spinner.stop()  # ocultar spinner
                email_final = email_detalle if email_detalle else email_listado
                # Guardar en log
                logging.info(f"Página {pagina} - Empresa {idx}: {nombre_completo}")
                logging.info(f"  Teléfono: {telefono if telefono else 'No disponible'}")
                logging.info(f"  Dirección: {direccion if direccion else 'No disponible'}")
                logging.info(f"  Email: {email_final if email_final else 'No disponible'}")
            else:
                email_final = email_listado
                logging.warning(f"Página {pagina} - Empresa {idx}: {nombre_completo} - Sin enlace de detalle")
            
            todos_registros.append([nombre, apellido, telefono, direccion, email_final])
            time.sleep(0.2)  # pausa entre empresas
        
        pagina += 1
        time.sleep(0.5)

    # Guardar CSV
    print("\n💾 Generando archivo CSV...")
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Nombre', 'Apellido', 'Teléfono', 'Dirección', 'Correo electrónico'])
        writer.writerows(todos_registros)
    
    print(f"\n✅ Extracción completada. {len(todos_registros)} registros guardados en {OUTPUT_CSV}")
    print(f"📝 Log detallado en: {LOG_FILE}")

if __name__ == "__main__":
    main()