"""
Standalone script for enhancing scanned PDFs with OCRmyPDF.
Adds a searchable text layer to PDF images, making them OCR-friendly.
"""
import sys
import argparse
from pathlib import Path
from services.ocrmypdf_processor import OCRmyPDFService


def main():
    parser = argparse.ArgumentParser(
        description="OCRmyPDF - Add searchable text layer to scanned PDFs"
    )
    
    parser.add_argument(
        "source",
        help="Source: either a directory with PDFs or a single PDF file"
    )
    
    parser.add_argument(
        "--output-dir",
        help="Output directory for processed PDFs (default: ocr_processed)",
        default="ocr_processed"
    )
    
    parser.add_argument(
        "--output-subdir",
        help="Optional subdirectory in output for organized output (e.g., 2020)",
        default=None
    )
    
    parser.add_argument(
        "--language",
        help="Language code for OCR (default: spa for Spanish, use 'eng' for English)",
        default="spa"
    )
    
    parser.add_argument(
        "--summary",
        help="Print detailed summary after processing",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    source_path = Path(args.source)
    
    if not source_path.exists():
        print(f"Error: Path not found: {args.source}")
        sys.exit(1)
    
    try:
        # Initialize service
        service = OCRmyPDFService(output_dir=args.output_dir)
        
        if source_path.is_file() and source_path.suffix.lower() == ".pdf":
            # Process single file
            print(f"Enhancing PDF: {source_path.name}")
            print(f"Language: {args.language}")
            print(f"Output directory: {args.output_dir}\n")
            
            result = service.enhance_pdf(
                str(source_path),
                args.output_subdir,
                args.language
            )
            
            if result["status"] == "success":
                print(f"✓ Successfully processed")
                print(f"  Input:  {source_path}")
                print(f"  Output: {result['output_path']}")
                print(f"  Size:   {result['file_size_kb']} KB")
            else:
                print(f"✗ Error: {result['message']}")
                sys.exit(1)
        
        elif source_path.is_dir():
            # Process all PDFs in directory
            print(f"Enhancing all PDFs in: {source_path}")
            print(f"Language: {args.language}")
            print(f"Output directory: {args.output_dir}")
            if args.output_subdir:
                print(f"Output subdirectory: {args.output_subdir}\n")
            
            results = service.enhance_directory(
                str(source_path),
                args.output_subdir,
                args.language
            )
            
            if args.summary:
                summary = service.processor.get_summary(results)
                
                print(f"\n{'='*60}")
                print("PROCESSING SUMMARY (OCRmyPDF)")
                print(f"{'='*60}")
                print(f"Total files processed: {summary['total_processed']}")
                print(f"Successful: {summary['successful']}")
                print(f"Failed: {summary['failed']}")
                print(f"Total size: {summary['total_size_kb']} KB")
                print(f"Output directory: {summary['output_directory']}")
                
                if summary['failed_files']:
                    print(f"\nFailed files:")
                    for filename in summary['failed_files']:
                        print(f"  - {filename}")
                
                if summary['failed'] > 0:
                    sys.exit(1)
        
        else:
            print(f"Error: Source must be a PDF file or directory containing PDFs")
            sys.exit(1)
    
    except RuntimeError as e:
        print(f"Error: {e}")
        print("\nInstall OCRmyPDF with:")
        print("  pip install ocrmypdf")
        print("\nAnd ensure you have installed:")
        print("  - Tesseract OCR: brew install tesseract")
        print("  - Ghostscript: brew install ghostscript")
        sys.exit(1)
    except Exception as e:
        print(f"Error during processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
