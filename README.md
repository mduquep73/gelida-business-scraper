# 🕷️ Gelida Business Scraper

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD](https://github.com/TU-USUARIO/gelida-business-scraper/actions/workflows/scraper_workflow.yml/badge.svg)](https://github.com/TU-USUARIO/gelida-business-scraper/actions/workflows/scraper_workflow.yml)

## 📋 Descripción

**Gelida Business Scraper** es una herramienta de automatización que extrae información pública de empresas y comercios del Ayuntamiento de Gelida (Barcelona, Cataluña). El script navega por todas las páginas del directorio, visita cada ficha de empresa y genera un archivo CSV estructurado con los datos de contacto.

### ✨ Características clave

- **Extracción completa** → Recorre automáticamente las 7 páginas del listado (103 empresas en total).
- **Datos precisos** → Obtiene **nombre**, **apellido**, **teléfono**, **dirección** y **correo electrónico**.
- **Respeto al servidor** → Pausas controladas entre peticiones (0.2–0.5 segundos).
- **Logs detallados** → Cada ejecución guarda un archivo de log con toda la información extraída.
- **Interfaz amigable** → Spinner animado en consola que muestra el progreso en tiempo real.
- **Automatizado con CI/CD** → Pipeline diario en GitHub Actions que ejecuta el scraper y publica los resultados.

## 🚀 Guía de inicio rápido

### Pre-requisitos

- Python 3.9 o superior
- `pip` (gestor de paquetes)

### Instalación y ejecución local

1. **Clona el repositorio**
   ```bash
   git clone https://github.com/mduquep73/gelida-business-scraper.git
   cd gelida-business-scraper
2. Crea y activa un entorno virtual (recomendado)
   python -m venv venv
   source venv/bin/activate        # En Linux/Mac
   venv\Scripts\activate           # En Windows
3. Instala las dependencias
   pip install -r requirements.txt
4. Ejecuta el scraper
   python src/scraper.py
Al finalizar, encontrarás el archivo data/directorio_gelida_final.csv y los logs en la carpeta logs/

⚙️ Automatización continua (CI/CD)

El proyecto incluye un pipeline de GitHub Actions que automatiza la ejecución del scraper. 
El flujo de trabajo:
    Se activa automáticamente todos los días a las 6:00 AM UTC (puedes cambiar el cron en el archivo YAML).
    También se puede ejecutar manualmente desde la pestaña "Actions" del repositorio.
Genera un artifact descargable (datos-del-scraper) que contiene el CSV y los logs de la última ejecución.
Los artifacts se conservan durante 30 días.
Puedes ver el estado del último workflow en el badge al inicio de este README.
📁 Estructura del proyecto
gelida-business-scraper/
├── mkdir   # Pipeline CI/CD
├── data/                          # Archivo CSV generado
├── logs/                          # Logs de cada ejecución
├── src/
│   └── scraper.py                 # Script principal
├── requirements.txt               # Dependencias
├── .gitignore                     # Archivos ignorados
├── LICENSE                        # Licencia MIT
└── README.md                      # Esta documentación

🛠️ Tecnologías utilizadas
   Python 3.9+ → Lenguaje principal.
   Requests → Peticiones HTTP.
   BeautifulSoup4 → Parseo de HTML.
   Logging estándar → Registro de eventos.
   GitHub Actions → Automatización y CI/CD.
📄 Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.
🤝 Contribuciones
Las contribuciones son bienvenidas. Si encuentras un error o deseas mejorar el código, por favor abre un issue o envía un pull request.
📧 Contacto
Para cualquier consulta, puedes abrir un issue en el repositorio.
⭐ Si este proyecto te ha sido útil, no olvides darle una estrella en GitHub.