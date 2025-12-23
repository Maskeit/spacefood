# 📋 INSTRUCCIONES DE USO - Sistema OCR de Procesamiento de PDFs

## 📖 Índice

1. [Descripción general](#descripción-general)
2. [Requisitos previos](#requisitos-previos)
3. [Servicios disponibles](#servicios-disponibles)
4. [Guía de uso paso a paso](#guía-de-uso-paso-a-paso)
5. [Ejemplos prácticos](#ejemplos-prácticos)
6. [Estructura de carpetas](#estructura-de-carpetas)
7. [Resolución de problemas](#resolución-de-problemas)

---

## 🎯 Descripción General

Este sistema procesa PDFs en 3 pasos independientes que pueden ejecutarse por separado:

```
PDF Escaneado
    ↓
[1. Mejora] → PDF Accesible (ocr_processed/)
    ↓
[2. OCR] → Texto extraído (data_result/{año}/)
    ↓
[3. Parse] → Datos JSON (invoices_json/{año}/)
```

**Cada paso es independiente y reutilizable:**
- Puedes mejorar PDFs sin extraer texto
- Puedes extraer texto sin mejora previa
- Puedes parsear archivos .txt existentes

---

## 📦 Requisitos Previos

### Instalación de dependencias del sistema

```bash
# Instalar Tesseract OCR con soporte de idiomas
brew install tesseract tesseract-lang

# Instalar Ghostscript
brew install ghostscript
```

### Instalación de paquetes Python

```bash
# Navega a la carpeta del proyecto
cd /Users/alejandre/Developer/jatenx/spacefood

# Instala los paquetes en el venv
pip install pytesseract pdf2image opencv-python pillow ocrmypdf
```

### Verificar instalación

```bash
# Verificar Tesseract
tesseract --version

# Verificar idiomas disponibles
tesseract --list-langs
```

Deberías ver `spa` en la lista de idiomas.

---

## 🛠️ Servicios Disponibles

### Servicio 1: Mejora de PDFs (OCRmyPDF)
**Script:** `1_enhance_pdf.py`
**Función:** Añade capa de texto invisible a PDFs escaneados
**Entrada:** PDF (solo imagen)
**Salida:** PDF accesible (con texto buscable)

### Servicio 2: Extracción OCR
**Script:** `2_extract_text.py`
**Función:** Extrae texto de PDFs y lo guarda en .txt
**Entrada:** PDF (accesible o mejorado)
**Salida:** Archivo .txt con texto extraído

### Servicio 3: Parseo a JSON
**Script:** `3_parse_to_json.py`
**Función:** Convierte texto OCR en datos estructurados JSON
**Entrada:** Archivo .txt (texto OCR)
**Salida:** Archivo .json con datos organizados

---

## 📝 Guía de Uso Paso a Paso

### ESCENARIO 1: PDF Escaneado Simple (Todos los pasos)

Si tienes un PDF escaneado (solo imágenes) y quieres obtener datos JSON:

#### Paso 1: Mejorar el PDF
```bash
python3 1_enhance_pdf.py /Users/alejandre/Developer/jatenx/spacefood/app/data/2020/4435.pdf \
  --output-subdir 2020 --language spa --summary
```

Este comando:
- ✓ Lee el PDF escaneado
- ✓ Añade capa de texto invisible
- ✓ Guarda en `ocr_processed/2020/`

#### Paso 2: Extraer texto OCR
```bash
python3 2_extract_text.py ocr_processed/2020 --summary
```

Este comando:
- ✓ Lee PDFs mejorados
- ✓ Extrae texto con OCR
- ✓ Guarda en `data_result/2020/`

#### Paso 3: Parsear a JSON
```bash
python3 3_parse_to_json.py data_result/2020 --output-subdir 2020 --summary
```

Este comando:
- ✓ Lee archivos .txt
- ✓ Extrae datos estructurados
- ✓ Guarda en `invoices_json/2020/`

---

### ESCENARIO 2: PDF Accesible (Sin mejora)

Si tu PDF ya tiene texto buscable, omite la mejora:

```bash
# Solo extraer texto
python3 2_extract_text.py /Users/alejandre/Developer/jatenx/spacefood/app/data/2020 --summary

# Luego parsear
python3 3_parse_to_json.py data_result/2020 --output-subdir 2020 --summary
```

---

### ESCENARIO 3: Procesar Carpeta Completa

#### Mejorar múltiples PDFs
```bash
python3 1_enhance_pdf.py /Users/alejandre/Developer/jatenx/spacefood/app/data/2020 \
  --output-subdir 2020 --language spa --summary
```

#### Extraer texto de todos
```bash
python3 2_extract_text.py ocr_processed/2020 --summary
```

#### Parsear todos los .txt
```bash
python3 3_parse_to_json.py data_result/2020 --output-subdir 2020 --summary
```

---

### ESCENARIO 4: Archivo .txt Existente

Si ya tienes un archivo .txt y solo quieres parsearlo:

```bash
# Un solo archivo
python3 3_parse_to_json.py data_result/2020/documento.txt --output-subdir 2020

# O toda una carpeta de .txt
python3 3_parse_to_json.py data_result/2020 --output-subdir 2020 --summary
```

---

## 💡 Ejemplos Prácticos

### Ejemplo 1: Un PDF individual

```bash
# Mejorar
python3 1_enhance_pdf.py /Users/alejandre/Developer/jatenx/spacefood/app/data/2020/4435.pdf \
  --output-subdir 2020

# Extraer
python3 2_extract_text.py ocr_processed/2020 --file 4435.pdf

# Parsear
python3 3_parse_to_json.py data_result/2020/4435.txt --output-subdir 2020
```

### Ejemplo 2: Año completo (2020)

```bash
# Mejorar todos los PDFs de 2020
python3 1_enhance_pdf.py /Users/alejandre/Developer/jatenx/spacefood/app/data/2020 \
  --output-subdir 2020 --summary

# Extraer de todos
python3 2_extract_text.py ocr_processed/2020 --summary

# Parsear todos los .txt
python3 3_parse_to_json.py data_result/2020 --output-subdir 2020 --summary
```

### Ejemplo 3: Solo parsear archivo existente

```bash
python3 3_parse_to_json.py data_result/2020/factura_001.txt \
  --output-subdir 2020 \
  --output-dir invoices_json
```

---

## 📁 Estructura de Carpetas

```
/Users/alejandre/Developer/jatenx/spacefood/app/

├── data/                          # PDFs ENTRADA
│   ├── 2020/
│   │   ├── 4435.pdf              # PDF escaneado
│   │   ├── 4436.pdf
│   │   └── ...
│   ├── 2021/
│   └── 2022/
│
├── ocr_processed/                 # PDFs MEJORADOS (salida paso 1)
│   ├── 2020/
│   │   ├── 4435.pdf              # PDF con capa de texto invisible
│   │   └── ...
│   └── 2021/
│
├── data_result/                   # TEXTO OCR EXTRAÍDO (salida paso 2)
│   ├── 2020/
│   │   ├── 4435.txt              # Texto extraído
│   │   └── ...
│   └── 2021/
│
├── invoices_json/                 # JSON PARSEADO (salida paso 3)
│   ├── 2020/
│   │   ├── 4435.json             # Datos estructurados
│   │   └── ...
│   └── 2021/
│
├── services/                      # Módulos Python
│   ├── ocrmypdf_processor.py
│   ├── ocr_processor.py
│   └── data_parser.py
│
└── Scripts de ejecución
    ├── 1_enhance_pdf.py           # Mejora PDFs
    ├── 2_extract_text.py          # Extrae texto OCR
    └── 3_parse_to_json.py         # Parsea a JSON
```

---

## 🐛 Resolución de Problemas

### Error: "tesseract is not installed"

```bash
brew install tesseract tesseract-lang
```

### Error: "language data for Spanish (spa) not found"

```bash
# Instala el paquete de idiomas
brew install tesseract-lang

# Verifica que spa está disponible
tesseract --list-langs | grep spa
```

### Error: "OCRmyPDF failed"

```bash
# Asegúrate de tener ghostscript
brew install ghostscript

# Verifica la instalación
ocrmypdf --version
```

### Error: "Module not found"

```bash
# Instala las dependencias Python
pip install pytesseract pdf2image opencv-python pillow ocrmypdf
```

### Los datos JSON están vacíos

Esto es normal con archivos completos. El parser está optimizado para:
- Importadores (nombre, RFC, domicilio)
- Facturas (número, fecha)
- Proveedores (nombre, país)
- Productos (descripción, cantidad)

Para mejorar la extracción, el texto OCR debe ser claro y estructurado.

---

## 🔄 Flujos de Trabajo Rápidos

### Flujo Rápido 1: PDF completo en 1 comando
```bash
# Combina mejora + OCR (sin parse)
python3 main.py process /ruta/pdf --summary
```

### Flujo Rápido 2: Solo mejorar
```bash
python3 1_enhance_pdf.py /ruta/pdf --summary
```

### Flujo Rápido 3: Solo extraer texto
```bash
python3 2_extract_text.py /ruta/pdf --summary
```

### Flujo Rápido 4: Solo parsear
```bash
python3 3_parse_to_json.py /ruta/txt --summary
```

---

## 📊 Resumen de Rutas Absolutas

Para la carpeta `/Users/alejandre/Developer/jatenx/spacefood/app/`:

| Acción | Comando |
|--------|---------|
| Mejorar PDFs 2020 | `python3 1_enhance_pdf.py /Users/alejandre/Developer/jatenx/spacefood/app/data/2020 --output-subdir 2020` |
| Extraer 2020 | `python3 2_extract_text.py ocr_processed/2020` |
| Parsear 2020 | `python3 3_parse_to_json.py data_result/2020 --output-subdir 2020` |

---

## ✅ Checklist de Verificación

Antes de procesar:

- [ ] ¿Tesseract instalado? `tesseract --version`
- [ ] ¿Español disponible? `tesseract --list-langs | grep spa`
- [ ] ¿Ghostscript instalado? `gs --version`
- [ ] ¿ocrmypdf instalado? `ocrmypdf --version`
- [ ] ¿Paquetes Python instalados? `pip list | grep pytesseract`
- [ ] ¿PDFs en carpeta data/? `ls /Users/alejandre/Developer/jatenx/spacefood/app/data/2020/`

---

## 📞 Soporte Rápido

**¿No se ve el resumen?** Agrega `--summary` a tu comando

**¿Procesar solo un archivo?** Usa `--file nombre.pdf` o `--file nombre.txt`

**¿Idioma diferente?** Usa `--language eng` (inglés), `--language fra` (francés), etc.

**¿Carpeta salida personalizada?** Usa `--output-dir /ruta/custom`

---

**Última actualización:** Diciembre 2025
