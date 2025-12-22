import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np
import os
from pathlib import Path
from typing import Dict, List
from services.data_parser import DataParserService


class OCRProcessor:
    """
    OCR Processor Service for handling PDF to text conversion.
    Processes multiple PDF files from a source directory and saves results to a destination directory.
    """

    def __init__(self, source_dir: str, output_dir: str = None):
        """
        Initialize the OCR Processor.
        
        Args:
            source_dir: Directory containing PDF files to process
            output_dir: Directory where results will be saved (defaults to parent/data_result/{year})
        """
        self.source_dir = Path(source_dir)
        self.output_dir = output_dir
        self.parser_service = DataParserService()
        
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {source_dir}")
    
    def _extract_year_from_path(self) -> str:
        """Extract year from source directory path."""
        parts = self.source_dir.parts
        for part in parts:
            if part.isdigit() and len(part) == 4 and 2000 <= int(part) <= 2100:
                return part
        return "unknown"
    
    def _get_output_directory(self) -> Path:
        """Determine the output directory based on source path structure."""
        if self.output_dir:
            return Path(self.output_dir)
        
        year = self._extract_year_from_path()
        # Navigate to parent of 'data' folder and create data_result/{year}
        parent_dir = self.source_dir.parent.parent
        output_path = parent_dir / "data_result" / year
        
        return output_path
    
    def _process_pdf(self, pdf_path: Path) -> str:
        """
        Perform OCR on a single PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text from the PDF
        """
        try:
            pages = convert_from_path(str(pdf_path))
            extracted_text = ""
            
            for page_num, page in enumerate(pages):
                # Convert page to numpy array for image processing
                page_arr = np.array(page)
                # Convert BGR to grayscale for better OCR accuracy
                gray_image = cv2.cvtColor(page_arr, cv2.COLOR_BGR2GRAY)
                
                # Perform OCR on the image
                text = pytesseract.image_to_string(gray_image)
                extracted_text += f"\n--- Page {page_num + 1} ---\n"
                extracted_text += text
            
            return extracted_text
        
        except Exception as e:
            raise Exception(f"Error processing PDF {pdf_path.name}: {str(e)}")
    
    def _save_result(self, pdf_path: Path, text_result: str) -> Path:
        """
        Save OCR result to a text file.
        
        Args:
            pdf_path: Path to the original PDF file
            text_result: Extracted text to save
            
        Returns:
            Path where the file was saved
        """
        output_dir = self._get_output_directory()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get filename without extension
        filename = pdf_path.stem
        output_path = output_dir / f"{filename}.txt"
        
        # Save the text result
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_result)
        
        return output_path
    
    def process_single_file(self, pdf_filename: str) -> Dict[str, str]:
        """
        Process a single PDF file by name.
        
        Args:
            pdf_filename: Name of the PDF file to process
            
        Returns:
            Dictionary with status and file path information
        """
        pdf_path = self.source_dir / pdf_filename
        
        if not pdf_path.exists():
            return {
                "status": "error",
                "filename": pdf_filename,
                "message": f"File not found: {pdf_path}"
            }
        
        try:
            text_result = self._process_pdf(pdf_path)
            output_path = self._save_result(pdf_path, text_result)
            
            return {
                "status": "success",
                "filename": pdf_filename,
                "output_path": str(output_path),
                "characters_extracted": len(text_result)
            }
        except Exception as e:
            return {
                "status": "error",
                "filename": pdf_filename,
                "message": str(e)
            }
    
    def process_directory(self) -> Dict[str, List[Dict]]:
        """
        Process all PDF files in the source directory.
        
        Returns:
            Dictionary with processing results for each file
        """
        pdf_files = sorted(self.source_dir.glob("*.pdf"))
        
        if not pdf_files:
            return {
                "status": "no_files",
                "message": f"No PDF files found in {self.source_dir}",
                "results": []
            }
        
        results = {
            "status": "processing",
            "source_directory": str(self.source_dir),
            "output_directory": str(self._get_output_directory()),
            "total_files": len(pdf_files),
            "results": []
        }
        
        for pdf_file in pdf_files:
            result = self.process_single_file(pdf_file.name)
            results["results"].append(result)
            
            # Print progress
            status = "✓" if result["status"] == "success" else "✗"
            print(f"{status} {pdf_file.name}")
        
        return results
    
    def get_summary(self, processing_results: Dict) -> Dict:
        """
        Generate a summary of processing results.
        
        Args:
            processing_results: Results from process_directory()
            
        Returns:
            Summary statistics
        """
        results = processing_results.get("results", [])
        successful = [r for r in results if r["status"] == "success"]
        failed = [r for r in results if r["status"] == "error"]
        
        return {
            "total_processed": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "output_directory": processing_results.get("output_directory"),
            "failed_files": [r["filename"] for r in failed]
        }

    def process_single_file_with_parsing(self, pdf_filename: str) -> Dict[str, str]:
        """
        Process a single PDF file and parse the extracted text to JSON.
        
        Args:
            pdf_filename: Name of the PDF file to process
            
        Returns:
            Dictionary with status and file path information (including JSON output)
        """
        # First, do the OCR
        ocr_result = self.process_single_file(pdf_filename)
        
        if ocr_result["status"] != "success":
            return ocr_result
        
        # Then parse the text file
        txt_path = Path(ocr_result["output_path"])
        year = self._extract_year_from_path()
        
        parse_result = self.parser_service.parse_txt_file(txt_path, output_subdir=year)
        
        return {
            "status": parse_result.get("status"),
            "filename": pdf_filename,
            "txt_path": ocr_result["output_path"],
            "json_path": parse_result.get("output_file", ""),
            "data": parse_result.get("data", {}),
            "message": parse_result.get("message", "")
        }
    
    def process_directory_with_parsing(self) -> Dict[str, List[Dict]]:
        """
        Process all PDF files in the source directory and parse results to JSON.
        
        Returns:
            Dictionary with processing results for each file (including parsed JSON)
        """
        pdf_files = sorted(self.source_dir.glob("*.pdf"))
        
        if not pdf_files:
            return {
                "status": "no_files",
                "message": f"No PDF files found in {self.source_dir}",
                "results": []
            }
        
        results = {
            "status": "processing_with_parsing",
            "source_directory": str(self.source_dir),
            "output_directory": str(self._get_output_directory()),
            "json_output_directory": str(Path("invoices_json") / self._extract_year_from_path()),
            "total_files": len(pdf_files),
            "results": []
        }
        
        for pdf_file in pdf_files:
            result = self.process_single_file_with_parsing(pdf_file.name)
            results["results"].append(result)
            
            # Print progress
            status = "✓" if result["status"] == "success" else "✗"
            print(f"{status} {pdf_file.name} -> {Path(result.get('json_path', '')).name if result.get('json_path') else 'error'}")
        
        return results
