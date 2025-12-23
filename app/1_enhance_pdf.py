"""
Script para mejorar PDFs escaneados añadiendo capa de texto invisible.
Convierte PDFs de solo imagen en PDFs accesibles y buscables.

ENTRADA: PDF escaneado (solo imagen)
SALIDA: PDF con capa de texto invisible
"""
import sys
import argparse
from pathlib import Path
from services.ocrmypdf_processor import OCRmyPDFService


def main():
    parser = argparse.ArgumentParser(
        description="Mejora PDFs escaneados añadiendo capa de texto invisible con OCRmyPDF"
    )
    
    parser.add_argument(
        "source",
        help="PDF o carpeta con PDFs escaneados"
    )
    
    parser.add_argument(
        "--output-dir",
        help="Carpeta donde guardar PDFs mejorados (default: ocr_processed)",
        default="ocr_processed"
    )
    
    parser.add_argument(
        "--output-subdir",
        help="Subcarpeta para organizar (ej: 2020)",
        default=None
    )
    
    parser.add_argument(
        "--language",
        help="Código de idioma (default: spa para español)",
        default="spa"
    )
    
    parser.add_argument(
        "--summary",
        help="Mostrar resumen detallado",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    source_path = Path(args.source)
    
    if not source_path.exists():
        print(f"Error: Archivo o carpeta no encontrada: {args.source}")
        sys.exit(1)
    
    try:
        service = OCRmyPDFService(output_dir=args.output_dir)
        
        if source_path.is_file() and source_path.suffix.lower() == ".pdf":
            print("Mejorando PDF: " + source_path.name)
            result = service.enhance_pdf(
                str(source_path),
                args.output_subdir,
                args.language
            )
            
            if result["status"] == "success":
                print(f"✓ Exitoso")
                print(f"  Entrada:  {source_path}")
                print(f"  Salida:   {result['output_path']}")
                print(f"  Tamaño:   {result['file_size_kb']} KB")
            else:
                print(f"✗ Error: {result['message']}")
                sys.exit(1)
        
        elif source_path.is_dir():
            print(f"Mejorando PDFs en: {source_path}")
            print(f"Idioma: {args.language}\n")
            
            results = service.enhance_directory(
                str(source_path),
                args.output_subdir,
                args.language
            )
            
            if args.summary:
                summary = service.processor.get_summary(results)
                print(f"\n{'='*60}")
                print("RESUMEN: Mejora de PDFs")
                print(f"{'='*60}")
                print(f"Total procesado: {summary['total_processed']}")
                print(f"Exitosos: {summary['successful']}")
                print(f"Errores: {summary['failed']}")
                print(f"Tamaño total: {summary['total_size_kb']} KB")
                print(f"Guardado en: {summary['output_directory']}")
                
                if summary['failed_files']:
                    print(f"\nArchivos con error:")
                    for f in summary['failed_files']:
                        print(f"  - {f}")
    
    except RuntimeError as e:
        print(f"Error: {e}")
        print("\nInstala con:")
        print("  pip install ocrmypdf")
        print("  brew install tesseract tesseract-lang")
        print("  brew install ghostscript")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
