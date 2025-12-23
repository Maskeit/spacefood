"""
Services Package - OCR Processing Pipeline
==========================================

Este paquete contiene tres servicios principales organizados por función:

1. PDF Enhancement Service (ocrmypdf_processor.py)
   - Mejora PDFs escaneados añadiendo capa de texto invisible
   - Entrada: PDF escaneado
   - Salida: PDF accesible con texto buscable

2. OCR Extraction Service (ocr_processor.py)
   - Extrae texto de PDFs y guarda en .txt
   - Entrada: PDF (mejorado o normal)
   - Salida: Archivo .txt con texto OCR

3. Data Parsing Service (data_parser.py)
   - Convierte texto OCR en datos estructurados JSON
   - Entrada: Archivo .txt con texto OCR
   - Salida: Archivo .json con datos extraídos

Flujo de trabajo típico:
  PDF escaneado → [Enhance] → PDF accesible → [OCR] → .txt → [Parse] → .json
"""
