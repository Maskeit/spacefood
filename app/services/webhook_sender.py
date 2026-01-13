"""
Webhook Sender Service for sending PDF files to n8n webhook.
Automates the process of sending OCR-processed PDFs for further processing.
"""
import requests
from pathlib import Path
from typing import Optional, List, Dict
import os
import time


class WebhookSenderService:
    """
    Service for sending PDF files to n8n webhook endpoint.
    """
    
    DEFAULT_WEBHOOK_URL = "https://n8n.jatenx.pro/webhook-test/e37077b5-31c1-4da2-aca9-ce0286b4ea3b"
    
    def __init__(self, webhook_url: str = None):
        """
        Initialize the Webhook Sender Service.
        
        Args:
            webhook_url: URL of the n8n webhook endpoint (uses default if not provided)
        """
        self.webhook_url = webhook_url or self.DEFAULT_WEBHOOK_URL
    
    def send_pdf(self, pdf_path: str, metadata: Dict = None) -> Dict:
        """
        Send a single PDF file to the webhook.
        
        Args:
            pdf_path: Path to the PDF file to send
            metadata: Optional metadata to include with the request
            
        Returns:
            Dict with response status and data
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            return {
                "success": False,
                "error": f"File not found: {pdf_path}",
                "file": str(pdf_path)
            }
        
        if not pdf_path.suffix.lower() == ".pdf":
            return {
                "success": False,
                "error": f"Not a PDF file: {pdf_path}",
                "file": str(pdf_path)
            }
        
        try:
            with open(pdf_path, "rb") as f:
                files = {
                    "file": (pdf_path.name, f, "application/pdf")
                }
                
                # Include metadata if provided
                data = metadata or {}
                data["filename"] = pdf_path.name
                data["filepath"] = str(pdf_path)
                
                response = requests.post(
                    self.webhook_url,
                    files=files,
                    data=data,
                    timeout=120  # 2 minutes timeout for large files
                )
                
                return {
                    "success": response.status_code in [200, 201, 202],
                    "status_code": response.status_code,
                    "response": response.text,
                    "file": pdf_path.name
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timeout",
                "file": pdf_path.name
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "file": pdf_path.name
            }
    
    def send_directory(
        self, 
        directory: str, 
        recursive: bool = False,
        delay_between: float = 1.0
    ) -> Dict:
        """
        Send all PDF files from a directory to the webhook.
        
        Args:
            directory: Path to directory containing PDF files
            recursive: Whether to search subdirectories
            delay_between: Delay in seconds between each file send (to avoid rate limiting)
            
        Returns:
            Dict with summary of all operations
        """
        directory = Path(directory)
        
        if not directory.exists():
            return {
                "success": False,
                "error": f"Directory not found: {directory}"
            }
        
        # Find all PDF files
        if recursive:
            pdf_files = list(directory.rglob("*.pdf"))
        else:
            pdf_files = list(directory.glob("*.pdf"))
        
        if not pdf_files:
            return {
                "success": True,
                "message": "No PDF files found",
                "total": 0,
                "sent": 0,
                "failed": 0
            }
        
        results = []
        sent_count = 0
        failed_count = 0
        
        print(f"📤 Sending {len(pdf_files)} PDF files to webhook...")
        print(f"   Webhook: {self.webhook_url}")
        print("-" * 50)
        
        for i, pdf_path in enumerate(pdf_files, 1):
            print(f"[{i}/{len(pdf_files)}] Sending: {pdf_path.name}...", end=" ")
            
            result = self.send_pdf(str(pdf_path))
            results.append(result)
            
            if result["success"]:
                print("✅")
                sent_count += 1
            else:
                print(f"❌ {result.get('error', 'Unknown error')}")
                failed_count += 1
            
            # Delay between files to avoid overwhelming the webhook
            if i < len(pdf_files) and delay_between > 0:
                time.sleep(delay_between)
        
        print("-" * 50)
        print(f"✅ Sent: {sent_count} | ❌ Failed: {failed_count} | Total: {len(pdf_files)}")
        
        return {
            "success": failed_count == 0,
            "total": len(pdf_files),
            "sent": sent_count,
            "failed": failed_count,
            "results": results
        }
    
    def send_year(self, year: str, base_dir: str = None) -> Dict:
        """
        Send all PDF files from a specific year's ocr_processed folder.
        
        Args:
            year: Year folder to process (e.g., "2024")
            base_dir: Base directory (defaults to app/ocr_processed)
            
        Returns:
            Dict with summary of operations
        """
        if base_dir is None:
            # Default to app/ocr_processed
            base_dir = Path(__file__).parent.parent / "ocr_processed"
        else:
            base_dir = Path(base_dir)
        
        year_dir = base_dir / year
        
        if not year_dir.exists():
            return {
                "success": False,
                "error": f"Year directory not found: {year_dir}"
            }
        
        print(f"\n📁 Processing year: {year}")
        return self.send_directory(str(year_dir))
    
    def send_all_years(self, base_dir: str = None) -> Dict:
        """
        Send all PDF files from all year folders in ocr_processed.
        
        Args:
            base_dir: Base directory (defaults to app/ocr_processed)
            
        Returns:
            Dict with summary of all operations by year
        """
        if base_dir is None:
            base_dir = Path(__file__).parent.parent / "ocr_processed"
        else:
            base_dir = Path(base_dir)
        
        if not base_dir.exists():
            return {
                "success": False,
                "error": f"Base directory not found: {base_dir}"
            }
        
        # Find all year directories
        year_dirs = [d for d in base_dir.iterdir() if d.is_dir() and d.name.isdigit()]
        year_dirs.sort(key=lambda x: x.name)
        
        if not year_dirs:
            return {
                "success": True,
                "message": "No year directories found",
                "years": []
            }
        
        results = {}
        total_sent = 0
        total_failed = 0
        
        for year_dir in year_dirs:
            result = self.send_year(year_dir.name, str(base_dir))
            results[year_dir.name] = result
            total_sent += result.get("sent", 0)
            total_failed += result.get("failed", 0)
        
        print("\n" + "=" * 50)
        print(f"📊 TOTAL: ✅ Sent: {total_sent} | ❌ Failed: {total_failed}")
        
        return {
            "success": total_failed == 0,
            "total_sent": total_sent,
            "total_failed": total_failed,
            "by_year": results
        }
