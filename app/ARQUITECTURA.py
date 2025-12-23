"""
Diagrama del sistema OCR - Estructura y flujos de datos
"""

ESTRUCTURA_VISUAL = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    SISTEMA OCR - ARQUITECTURA                              ║
╚════════════════════════════════════════════════════════════════════════════╝

┌─ ENTRADA ─────────────────────────────────────────────────────────────────┐
│                                                                             │
│  data/2020/                                                                 │
│  ├── 4435.pdf  (PDF escaneado - solo imágenes)                            │
│  ├── 4436.pdf                                                              │
│  └── ...                                                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
              ↓
       [SERVICIO 1]
    1_enhance_pdf.py
     (OCRmyPDF)
       
┌─ PASO 1: MEJORA ──────────────────────────────────────────────────────────┐
│                                                                             │
│  Función: Añadir capa de texto invisible                                   │
│  Entrada:  PDF escaneado (solo imagen)                                    │
│  Salida:   PDF accesible (con texto buscable)                             │
│                                                                             │
│  Comando:                                                                   │
│  python3 1_enhance_pdf.py /ruta/pdf --summary                             │
│                                                                             │
│  Resultado:                                                                 │
│  ocr_processed/2020/4435.pdf  ← PDF mejorado                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
              ↓
       [SERVICIO 2]
    2_extract_text.py
      (pytesseract)
       
┌─ PASO 2: EXTRACCIÓN OCR ──────────────────────────────────────────────────┐
│                                                                             │
│  Función: Extraer texto de PDF                                            │
│  Entrada:  PDF (accesible o mejorado)                                     │
│  Salida:   Archivo .txt con texto extraído                                │
│                                                                             │
│  Comando:                                                                   │
│  python3 2_extract_text.py /ruta/pdf --summary                            │
│                                                                             │
│  Resultado:                                                                 │
│  data_result/2020/4435.txt  ← Texto extraído                              │
│  (contiene: texto OCR sin procesar)                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
              ↓
       [SERVICIO 3]
    3_parse_to_json.py
      (DataParser)
       
┌─ PASO 3: PARSEO ──────────────────────────────────────────────────────────┐
│                                                                             │
│  Función: Convertir texto en datos estructurados                          │
│  Entrada:  Archivo .txt (texto OCR)                                       │
│  Salida:   Archivo .json (datos estructurados)                            │
│                                                                             │
│  Comando:                                                                   │
│  python3 3_parse_to_json.py /ruta/txt --summary                           │
│                                                                             │
│  Resultado:                                                                 │
│  invoices_json/2020/4435.json  ← Datos extraídos                          │
│  (contiene: importador, factura, proveedor, partidas)                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
              ↓
┌─ SALIDA FINAL ────────────────────────────────────────────────────────────┐
│                                                                             │
│  invoices_json/2020/4435.json                                             │
│  {                                                                          │
│    "importador_nombre": "MICRO HERROS DE OCCIDENTE S.A.",                 │
│    "importador_rfc": "MHO921021UD0",                                      │
│    "proveedores": [...],                                                   │
│    "partidas": [...]                                                       │
│  }                                                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘


╔════════════════════════════════════════════════════════════════════════════╗
║                      SERVICIOS INDEPENDIENTES                              ║
╚════════════════════════════════════════════════════════════════════════════╝

ESCENARIO A: Solo mejorar PDFs
┌─────────────────────────────────────────┐
│  data/*.pdf                              │
│         ↓                                │
│  [1_enhance_pdf.py]                     │
│         ↓                                │
│  ocr_processed/*.pdf                    │
└─────────────────────────────────────────┘


ESCENARIO B: Solo extraer texto
┌─────────────────────────────────────────┐
│  data/*.pdf (accesibles)                │
│         ↓                                │
│  [2_extract_text.py]                    │
│         ↓                                │
│  data_result/*.txt                      │
└─────────────────────────────────────────┘


ESCENARIO C: Solo parsear existentes
┌─────────────────────────────────────────┐
│  data_result/*.txt                      │
│         ↓                                │
│  [3_parse_to_json.py]                   │
│         ↓                                │
│  invoices_json/*.json                   │
└─────────────────────────────────────────┘


╔════════════════════════════════════════════════════════════════════════════╗
║                        ARCHIVOS DEL SISTEMA                                ║
╚════════════════════════════════════════════════════════════════════════════╝

SCRIPTS DE EJECUCIÓN:
├── 1_enhance_pdf.py        → Mejora PDFs con OCRmyPDF
├── 2_extract_text.py       → Extrae texto con Tesseract
├── 3_parse_to_json.py      → Parsea texto a JSON
├── main.py                 → Interfaz unificada (alternativa)
├── list_folders.py         → Listar carpetas disponibles
└── ejemplo_flujos.sh       → Ejemplos de comandos

SERVICIOS (módulos Python):
└── services/
    ├── ocrmypdf_processor.py    → Clase OCRmyPDFService
    ├── ocr_processor.py         → Clase OCRProcessor
    ├── data_parser.py           → Clase DataParserService
    └── README.md                → Descripción técnica

DOCUMENTACIÓN:
├── INSTRUCCIONES.md         → Guía completa (LEER PRIMERO)
├── app/README.md            → Resumen rápido
└── app/services/README.md   → Descripción técnica


╔════════════════════════════════════════════════════════════════════════════╗
║                        CARPETAS DE DATOS                                   ║
╚════════════════════════════════════════════════════════════════════════════╝

ESTRUCTURA DE CARPETAS ESPERADA:

app/
├── data/                ← ENTRADA (PDFs)
│   ├── 2020/
│   │   ├── 4435.pdf
│   │   └── 4436.pdf
│   ├── 2021/
│   └── 2022/
│
├── ocr_processed/       ← PASO 1 (PDFs mejorados)
│   ├── 2020/
│   │   ├── 4435.pdf     (con capa de texto)
│   │   └── 4436.pdf
│   └── 2021/
│
├── data_result/         ← PASO 2 (Texto extraído)
│   ├── 2020/
│   │   ├── 4435.txt     (texto OCR)
│   │   └── 4436.txt
│   └── 2021/
│
└── invoices_json/       ← PASO 3 (JSON final)
    ├── 2020/
    │   ├── 4435.json    (datos estructurados)
    │   └── 4436.json
    └── 2021/


╔════════════════════════════════════════════════════════════════════════════╗
║                        COMANDOS RÁPIDOS                                    ║
╚════════════════════════════════════════════════════════════════════════════╝

# Procesar un PDF individual completo
python3 1_enhance_pdf.py /ruta/pdf
python3 2_extract_text.py ocr_processed/año
python3 3_parse_to_json.py data_result/año/archivo.txt

# Procesar carpeta completa
python3 1_enhance_pdf.py /ruta/carpeta --summary
python3 2_extract_text.py ocr_processed/año --summary
python3 3_parse_to_json.py data_result/año --summary

# Solo un servicio
python3 2_extract_text.py /ruta/pdf --summary
python3 3_parse_to_json.py /ruta/txt --summary

# Ver carpetas disponibles
python3 list_folders.py


╔════════════════════════════════════════════════════════════════════════════╗
║                    REQUISITOS PREVIOS                                      ║
╚════════════════════════════════════════════════════════════════════════════╝

Sistema:
  brew install tesseract tesseract-lang ghostscript

Python:
  pip install pytesseract pdf2image opencv-python pillow ocrmypdf

Verificar:
  tesseract --list-langs    (debe incluir 'spa')
  ocrmypdf --version        (debe funcionar)
"""

if __name__ == "__main__":
    print(ESTRUCTURA_VISUAL)
