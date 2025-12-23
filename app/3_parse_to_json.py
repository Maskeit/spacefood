"""
Script para parsear archivos .txt a JSON estructurado.
Extrae datos específicos del texto OCR y los organiza en JSON.

ENTRADA: Archivo .txt con texto OCR o carpeta con múltiples .txt
SALIDA: Archivo .json con datos estructurados
"""
import sys
import argparse
from pathlib import Path
import json
from services.data_parser import DataParserService


def main():
    parser = argparse.ArgumentParser(
        description="Convierte archivos .txt OCR en JSON estructurado"
    )
    
    parser.add_argument(
        "source",
        help="Archivo .txt o carpeta con archivos .txt"
    )
    
    parser.add_argument(
        "--output-subdir",
        help="Subcarpeta para organizar JSONs (ej: 2020)",
        default=None
    )
    
    parser.add_argument(
        "--output-dir",
        help="Carpeta base para guardar JSONs (default: invoices_json)",
        default="invoices_json"
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
        parser_service = DataParserService(output_base_dir=args.output_dir)
        
        if source_path.is_file() and source_path.suffix == ".txt":
            print(f"Parseando archivo: {source_path.name}\n")
            result = parser_service.parse_txt_file(source_path, args.output_subdir)
            
            if result["status"] == "success":
                print(f"✓ Exitoso")
                print(f"  Entrada:  {source_path}")
                print(f"  Salida:   {result['output_file']}")
                print(f"\nDatos extraídos:")
                print(json.dumps(result['data'], indent=2, ensure_ascii=False))
            else:
                print(f"✗ Error: {result['message']}")
                sys.exit(1)
        
        elif source_path.is_dir():
            print(f"Parseando archivos .txt en: {source_path}\n")
            txt_files = sorted(source_path.glob("*.txt"))
            
            if not txt_files:
                print(f"No hay archivos .txt en {source_path}")
                sys.exit(1)
            
            results = []
            for txt_file in txt_files:
                result = parser_service.parse_txt_file(txt_file, args.output_subdir)
                results.append(result)
                
                status = "✓" if result["status"] == "success" else "✗"
                print(f"{status} {txt_file.name}")
            
            if args.summary:
                successful = [r for r in results if r["status"] == "success"]
                failed = [r for r in results if r["status"] == "error"]
                
                print(f"\n{'='*60}")
                print("RESUMEN: Parseo a JSON")
                print(f"{'='*60}")
                print(f"Total procesado: {len(results)}")
                print(f"Exitosos: {len(successful)}")
                print(f"Errores: {len(failed)}")
                print(f"Carpeta salida: {args.output_dir}")
                
                if failed:
                    print(f"\nArchivos con error:")
                    for r in failed:
                        print(f"  - {Path(r.get('source_file', 'unknown')).name}: {r.get('message')}")
        
        else:
            print("Error: Debe ser un archivo .txt o una carpeta")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
