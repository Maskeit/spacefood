#!/bin/bash
# ejemplo_flujos.sh - Ejemplos de uso del sistema OCR

echo "=========================================="
echo "EJEMPLOS DE USO - Sistema OCR"
echo "=========================================="
echo ""

# NOTA: Descomenta los comandos que quieras ejecutar

# ============================================
# ESCENARIO 1: PDF Individual Completo
# ============================================
echo "ESCENARIO 1: Procesar un PDF individual"
echo "------------------------------------------"
echo ""
echo "# Paso 1: Mejorar PDF"
echo "python3 1_enhance_pdf.py /Users/alejandre/Developer/jatenx/spacefood/app/data/2020/4435.pdf --output-subdir 2020 --language spa"
echo ""
echo "# Paso 2: Extraer texto"
echo "python3 2_extract_text.py ocr_processed/2020 --file 4435.pdf"
echo ""
echo "# Paso 3: Parsear a JSON"
echo "python3 3_parse_to_json.py data_result/2020/4435.txt --output-subdir 2020"
echo ""
echo ""

# ============================================
# ESCENARIO 2: Carpeta Completa (2020)
# ============================================
echo "ESCENARIO 2: Procesar todos los PDFs de 2020"
echo "------------------------------------------"
echo ""
echo "# Paso 1: Mejorar todos"
echo "python3 1_enhance_pdf.py /Users/alejandre/Developer/jatenx/spacefood/app/data/2020 --output-subdir 2020 --summary"
echo ""
echo "# Paso 2: Extraer todos"
echo "python3 2_extract_text.py ocr_processed/2020 --summary"
echo ""
echo "# Paso 3: Parsear todos"
echo "python3 3_parse_to_json.py data_result/2020 --output-subdir 2020 --summary"
echo ""
echo ""

# ============================================
# ESCENARIO 3: Solo mejora
# ============================================
echo "ESCENARIO 3: Solo mejorar PDFs (sin OCR)"
echo "------------------------------------------"
echo ""
echo "python3 1_enhance_pdf.py /Users/alejandre/Developer/jatenx/spacefood/app/data/2020 --output-subdir 2020 --summary"
echo ""
echo ""

# ============================================
# ESCENARIO 4: Solo OCR
# ============================================
echo "ESCENARIO 4: Solo extraer texto (PDFs ya accesibles)"
echo "------------------------------------------"
echo ""
echo "python3 2_extract_text.py /Users/alejandre/Developer/jatenx/spacefood/app/data/2020 --summary"
echo ""
echo ""

# ============================================
# ESCENARIO 5: Solo parseo
# ============================================
echo "ESCENARIO 5: Solo parsear archivos .txt existentes"
echo "------------------------------------------"
echo ""
echo "python3 3_parse_to_json.py data_result/2020 --output-subdir 2020 --summary"
echo ""
echo ""

# ============================================
# ESCENARIO 6: Múltiples años
# ============================================
echo "ESCENARIO 6: Procesar múltiples años (2020-2023)"
echo "------------------------------------------"
echo ""
echo "for year in 2020 2021 2022 2023; do"
echo "  echo \"Procesando \$year...\""
echo "  python3 1_enhance_pdf.py /Users/alejandre/Developer/jatenx/spacefood/app/data/\$year --output-subdir \$year --summary"
echo "  python3 2_extract_text.py ocr_processed/\$year --summary"
echo "  python3 3_parse_to_json.py data_result/\$year --output-subdir \$year --summary"
echo "done"
echo ""
echo ""

# ============================================
# INFORMACIÓN ÚTIL
# ============================================
echo "=========================================="
echo "INFORMACIÓN ÚTIL"
echo "=========================================="
echo ""
echo "Para ver resumen de archivos disponibles:"
echo "  python3 list_folders.py"
echo ""
echo "Para ver esta ayuda:"
echo "  cat ejemplo_flujos.sh"
echo ""
echo "Idiomas disponibles para OCR:"
echo "  tesseract --list-langs"
echo ""
echo "Para procesar con idioma diferente a español:"
echo "  python3 1_enhance_pdf.py /ruta --language eng  # inglés"
echo "  python3 1_enhance_pdf.py /ruta --language fra  # francés"
echo ""
