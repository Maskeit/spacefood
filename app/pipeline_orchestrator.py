"""
Pipeline orchestrator - Ejecuta flujos de trabajo completos de OCR.
Combina los tres servicios en pipelines predefinidos.
"""
import sys
from pathlib import Path
from services.ocrmypdf_processor import OCRmyPDFService
from services.ocr_processor import OCRProcessor
from services.data_parser import DataParserService


class OCRPipeline:
    """Orquestador de pipeline completo de OCR."""
    
    def __init__(self):
        self.ocrmypdf_service = None
        self.parser_service = DataParserService()
    
    def enhance_only(self, source_dir: str, output_dir: str = "ocr_processed") -> dict:
        """
        Ejecutar solo mejora de PDFs con OCRmyPDF.
        Útil para: PDFs escaneados que necesitan mejora antes de OCR
        """
        print("=" * 70)
        print("PASO 1: Mejora de PDFs (OCRmyPDF)")
        print("=" * 70)
        print(f"Entrada:  PDFs escaneados en {source_dir}")
        print(f"Salida:   PDFs accesibles en {output_dir}\n")
        
        self.ocrmypdf_service = OCRmyPDFService(output_dir=output_dir)
        results = self.ocrmypdf_service.enhance_directory(source_dir, language="spa")
        return results
    
    def ocr_only(self, source_dir: str, output_dir: str = None) -> dict:
        """
        Ejecutar solo extracción de texto OCR.
        Útil para: PDFs ya accesibles o mejorados previamente
        """
        print("=" * 70)
        print("PASO 1: Extracción de texto OCR")
        print("=" * 70)
        print(f"Entrada:  PDFs en {source_dir}")
        print(f"Salida:   Archivos .txt en data_result/\n")
        
        processor = OCRProcessor(source_dir, output_dir)
        results = processor.process_directory()
        return results
    
    def parse_only(self, source_dir: str) -> dict:
        """
        Ejecutar solo parseo de texto a JSON.
        Útil para: Procesar archivos .txt existentes
        """
        print("=" * 70)
        print("PASO 1: Parseo de texto a JSON")
        print("=" * 70)
        print(f"Entrada:  Archivos .txt en {source_dir}")
        print(f"Salida:   Archivos .json en invoices_json/\n")
        
        txt_files = sorted(Path(source_dir).glob("*.txt"))
        results = {"total": len(txt_files), "processed": []}
        
        for txt_file in txt_files:
            result = self.parser_service.parse_txt_file(txt_file)
            results["processed"].append(result)
            status = "✓" if result["status"] == "success" else "✗"
            print(f"{status} {txt_file.name}")
        
        return results
    
    def enhance_then_ocr(self, source_dir: str, enhance_output: str = "ocr_processed") -> dict:
        """
        Ejecutar 2 pasos: Mejora + OCR
        Útil para: PDFs escaneados que necesitan mejora antes de extraer texto
        """
        print("=" * 70)
        print("PIPELINE: Mejora + OCR")
        print("=" * 70)
        
        # Paso 1: Mejora
        print("\nPASO 1: Mejora de PDFs (OCRmyPDF)")
        print("-" * 70)
        enhance_results = self.enhance_only(source_dir, enhance_output)
        
        # Paso 2: OCR
        print("\nPASO 2: Extracción de texto OCR")
        print("-" * 70)
        ocr_results = self.ocr_only(enhance_output)
        
        return {
            "step_1_enhance": enhance_results,
            "step_2_ocr": ocr_results
        }
    
    def ocr_then_parse(self, source_dir: str, txt_output: str = None) -> dict:
        """
        Ejecutar 2 pasos: OCR + Parse
        Útil para: PDFs accesibles que necesitan extracción de datos estructurados
        """
        print("=" * 70)
        print("PIPELINE: OCR + Parse")
        print("=" * 70)
        
        # Paso 1: OCR
        print("\nPASO 1: Extracción de texto OCR")
        print("-" * 70)
        processor = OCRProcessor(source_dir, txt_output)
        ocr_results = processor.process_directory()
        txt_output_dir = processor._get_output_directory()
        
        # Paso 2: Parse
        print("\nPASO 2: Parseo de texto a JSON")
        print("-" * 70)
        parse_results = self.parse_only(str(txt_output_dir))
        
        return {
            "step_1_ocr": ocr_results,
            "step_2_parse": parse_results
        }
    
    def enhance_ocr_parse(self, source_dir: str, enhance_output: str = "ocr_processed") -> dict:
        """
        Ejecutar 3 pasos completos: Mejora + OCR + Parse
        Útil para: PDFs escaneados que necesitan convertirse en datos estructurados
        """
        print("=" * 70)
        print("PIPELINE COMPLETO: Mejora + OCR + Parse")
        print("=" * 70)
        
        # Paso 1: Mejora
        print("\nPASO 1: Mejora de PDFs (OCRmyPDF)")
        print("-" * 70)
        enhance_results = self.enhance_only(source_dir, enhance_output)
        
        # Paso 2: OCR
        print("\nPASO 2: Extracción de texto OCR")
        print("-" * 70)
        ocr_results = self.ocr_only(enhance_output)
        processor = OCRProcessor(enhance_output)
        txt_output_dir = processor._get_output_directory()
        
        # Paso 3: Parse
        print("\nPASO 3: Parseo de texto a JSON")
        print("-" * 70)
        parse_results = self.parse_only(str(txt_output_dir))
        
        return {
            "step_1_enhance": enhance_results,
            "step_2_ocr": ocr_results,
            "step_3_parse": parse_results
        }
