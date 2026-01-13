"""
Script para extraer texto de PDFs mediante OCR.
Convierte PDFs en archivos .txt con el texto extraído.

ENTRADA: PDF (accesible o mejorado)
CREAR: carpeta data_result/ con archivos .txt
SALIDA: Archivo .txt con texto extraído
"""
import sys
import argparse
from pathlib import Path
from services.ocr_processor import OCRProcessor


def main():
    parser = argparse.ArgumentParser(
        description="Extrae texto de PDFs mediante OCR y lo guarda en archivos .txt"
    )
    
    parser.add_argument(
        "source_dir",
        help="Carpeta con PDFs para procesar"
    )
    
    parser.add_argument(
        "--file",
        help="Procesar solo un archivo (ej: documento.pdf)",
        default=None
    )
    
    parser.add_argument(
        "--output-dir",
        help="Carpeta personalizada para archivos .txt",
        default=None
    )
    
    parser.add_argument(
        "--summary",
        help="Mostrar resumen detallado",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    source_path = Path(args.source_dir)
    
    if not source_path.exists():
        print(f"Error: Carpeta no encontrada: {args.source_dir}")
        sys.exit(1)
    
    if not source_path.is_dir():
        print(f"Error: No es una carpeta: {args.source_dir}")
        sys.exit(1)
    
    try:
        processor = OCRProcessor(str(source_path), args.output_dir)
        
        print(f"Extrayendo texto de PDFs...")
        print(f"Entrada:   {source_path}")
        print(f"Salida:    {processor._get_output_directory()}\n")
        
        if args.file:
            print(f"Procesando: {args.file}\n")
            result = processor.process_single_file(args.file)
            print(f"Estado: {result['status']}")
            if result['status'] == 'success':
                print(f"✓ Exitoso")
                print(f"  Caracteres extraídos: {result['characters_extracted']}")
                print(f"  Guardado en: {result['output_path']}")
            else:
                print(f"✗ Error: {result['message']}")
                sys.exit(1)
        else:
            print("Procesando todos los PDFs...\n")
            results = processor.process_directory()
            
            if args.summary:
                summary = processor.get_summary(results)
                print(f"\n{'='*60}")
                print("RESUMEN: Extracción OCR")
                print(f"{'='*60}")
                print(f"Total procesado: {summary['total_processed']}")
                print(f"Exitosos: {summary['successful']}")
                print(f"Errores: {summary['failed']}")
                print(f"Carpeta salida: {summary['output_directory']}")
                
                if summary['failed_files']:
                    print(f"\nArchivos con error:")
                    for f in summary['failed_files']:
                        print(f"  - {f}")
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
