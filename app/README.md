# OCR Pipeline - Sistema de Procesamiento de PDFs

## 🚀 Inicio Rápido

```bash
# Mejorar PDF escaneado
python3 1_enhance_pdf.py /ruta/pdf

# Extraer texto
python3 2_extract_text.py /ruta/pdf --summary

# Parsear a JSON
python3 3_parse_to_json.py /ruta/txt --summary
```

## 📂 Scripts Disponibles

| Script | Función | Entrada | Salida |
|--------|---------|---------|--------|
| `1_enhance_pdf.py` | Mejora PDFs escaneados | PDF | PDF mejorado |
| `2_extract_text.py` | Extrae texto OCR | PDF | .txt |
| `3_parse_to_json.py` | Parsea a JSON | .txt | .json |

## 📖 Documentación Completa

Ver **INSTRUCCIONES.md** en la raíz del proyecto para:
- Guía detallada de cada servicio
- Ejemplos de todos los escenarios
- Requisitos previos
- Solución de problemas

## 🔧 Servicios

```
services/
├── ocrmypdf_processor.py      # Mejora PDFs
├── ocr_processor.py           # Extrae texto
└── data_parser.py             # Parsea JSON
```

## 📊 Flujo de Datos

```
data/2020/*.pdf
    ↓ [1_enhance_pdf.py]
ocr_processed/2020/*.pdf
    ↓ [2_extract_text.py]
data_result/2020/*.txt
    ↓ [3_parse_to_json.py]
invoices_json/2020/*.json
```

---

**Ver INSTRUCCIONES.md para documentación completa**
