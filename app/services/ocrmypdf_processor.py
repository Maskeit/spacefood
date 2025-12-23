"""
OCRmyPDF Processor Service for adding searchable text layers to scanned PDFs.
This service uses ocrmypdf to enhance PDFs before OCR text extraction.
"""
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OCRmyPDFProcessor:
    """
    Processor service that uses OCRmyPDF to add searchable text layers to PDFs.
    Useful for pre-processing scanned PDFs before text extraction.
    """

    def __init__(self, output_dir: str = "ocr_processed"):
        """
        Initialize the OCRmyPDF Processor.

        Args:
            output_dir: Directory where processed PDFs will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if ocrmypdf is installed
        if not self._check_ocrmypdf_installed():
            raise RuntimeError(
                "OCRmyPDF is not installed. "
                "Install with: pip install ocrmypdf\n"
                "Also requires: Tesseract OCR and Ghostscript"
            )

    @staticmethod
    def _check_ocrmypdf_installed() -> bool:
        """Check if ocrmypdf command is available."""
        try:
            result = subprocess.run(
                ["ocrmypdf", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _process_pdf(self, pdf_path: Path, output_path: Path, language: str = "spa") -> Dict[str, str]:
        """
        Process a single PDF with OCRmyPDF.

        Args:
            pdf_path: Path to input PDF
            output_path: Path where processed PDF will be saved
            language: Language code for OCR (default: Spanish)

        Returns:
            Dictionary with status and details
        """
        try:
            # Build ocrmypdf command
            cmd = [
                "ocrmypdf",
                "--language", language,
                "--force-ocr",  # Always perform OCR even if text exists
                "--output-type", "pdf",  # Output as PDF
                str(pdf_path),
                str(output_path)
            ]

            logger.info(f"Processing: {pdf_path.name}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per file
            )

            if result.returncode == 0:
                file_size_kb = output_path.stat().st_size / 1024
                return {
                    "status": "success",
                    "filename": pdf_path.name,
                    "output_path": str(output_path),
                    "file_size_kb": round(file_size_kb, 2)
                }
            else:
                return {
                    "status": "error",
                    "filename": pdf_path.name,
                    "message": f"OCRmyPDF failed: {result.stderr}"
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "filename": pdf_path.name,
                "message": "Processing timeout (file may be too large)"
            }
        except Exception as e:
            return {
                "status": "error",
                "filename": pdf_path.name,
                "message": str(e)
            }

    def process_single_file(
        self,
        pdf_path: Path,
        output_subdir: str = None,
        language: str = "spa"
    ) -> Dict[str, str]:
        """
        Process a single PDF file.

        Args:
            pdf_path: Path to input PDF
            output_subdir: Optional subdirectory for output (e.g., '2020')
            language: Language code for OCR

        Returns:
            Dictionary with processing result
        """
        if not pdf_path.exists():
            return {
                "status": "error",
                "filename": pdf_path.name,
                "message": f"File not found: {pdf_path}"
            }

        # Determine output directory
        if output_subdir:
            output_dir = self.output_dir / output_subdir
        else:
            output_dir = self.output_dir

        output_dir.mkdir(parents=True, exist_ok=True)

        # Create output path
        output_path = output_dir / pdf_path.name

        return self._process_pdf(pdf_path, output_path, language)

    def process_directory(
        self,
        source_dir: Path,
        output_subdir: str = None,
        language: str = "spa"
    ) -> Dict[str, List[Dict]]:
        """
        Process all PDF files in a directory.

        Args:
            source_dir: Directory containing PDFs to process
            output_subdir: Optional subdirectory for output
            language: Language code for OCR

        Returns:
            Dictionary with processing results for each file
        """
        pdf_files = sorted(source_dir.glob("*.pdf"))

        if not pdf_files:
            return {
                "status": "no_files",
                "message": f"No PDF files found in {source_dir}",
                "results": []
            }

        # Determine output directory
        if output_subdir:
            output_dir = self.output_dir / output_subdir
        else:
            output_dir = self.output_dir

        results = {
            "status": "processing",
            "source_directory": str(source_dir),
            "output_directory": str(output_dir),
            "total_files": len(pdf_files),
            "language": language,
            "results": []
        }

        print(f"\nProcessing {len(pdf_files)} PDF files with OCRmyPDF...\n")

        for pdf_file in pdf_files:
            result = self.process_single_file(pdf_file, output_subdir, language)
            results["results"].append(result)

            status = "✓" if result["status"] == "success" else "✗"
            if result["status"] == "success":
                print(f"{status} {pdf_file.name} ({result['file_size_kb']} KB)")
            else:
                print(f"{status} {pdf_file.name} - Error: {result.get('message', 'Unknown')}")

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

        total_size = sum(r.get("file_size_kb", 0) for r in successful)

        return {
            "total_processed": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "total_size_kb": round(total_size, 2),
            "output_directory": processing_results.get("output_directory"),
            "failed_files": [r.get("filename") for r in failed]
        }


class OCRmyPDFService:
    """Wrapper service for convenient OCRmyPDF operations."""

    def __init__(self, output_dir: str = "ocr_processed"):
        """
        Initialize the OCRmyPDF Service.

        Args:
            output_dir: Base directory for processed PDFs
        """
        self.processor = OCRmyPDFProcessor(output_dir)

    def enhance_pdf(
        self,
        pdf_path: str,
        output_subdir: str = None,
        language: str = "spa"
    ) -> Dict[str, str]:
        """
        Enhance a single PDF with searchable text layer.

        Args:
            pdf_path: Path to input PDF
            output_subdir: Optional subdirectory for output
            language: Language code for OCR

        Returns:
            Processing result dictionary
        """
        path = Path(pdf_path)
        return self.processor.process_single_file(path, output_subdir, language)

    def enhance_directory(
        self,
        source_dir: str,
        output_subdir: str = None,
        language: str = "spa"
    ) -> Dict[str, List[Dict]]:
        """
        Enhance all PDFs in a directory.

        Args:
            source_dir: Directory with PDFs to process
            output_subdir: Optional subdirectory for output
            language: Language code for OCR

        Returns:
            Processing results dictionary
        """
        path = Path(source_dir)
        return self.processor.process_directory(path, output_subdir, language)

    def get_output_directory(self) -> Path:
        """Get the base output directory for processed PDFs."""
        return self.processor.output_dir
