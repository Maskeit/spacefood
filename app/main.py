"""
Main entry point for OCR batch processing.
Allows flexible folder-based processing with simple CLI interface.
"""
import sys
import argparse
from pathlib import Path
import json
import os
from services.ocr_processor import OCRProcessor
from services.data_parser import DataParserService


def resolve_path(path_str: str) -> Path:
    """
    Resolve a path that can be absolute or relative.
    If relative, resolve from the current working directory.
    If absolute, use as-is.
    """
    path = Path(path_str)
    
    # If it's already absolute, return it
    if path.is_absolute():
        return path
    
    # Otherwise, make it absolute relative to cwd
    return Path.cwd() / path


def main():
    parser = argparse.ArgumentParser(
        description="OCR Batch Processor - Process PDF files from a directory"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # OCR command
    ocr_parser = subparsers.add_parser("ocr", help="Process PDFs to extract text")
    ocr_parser.add_argument(
        "source_dir",
        help="Source directory containing PDF files to process (absolute or relative path)"
    )
    ocr_parser.add_argument(
        "--output-dir",
        help="Optional custom output directory (defaults to app/data_result/{year})",
        default=None
    )
    ocr_parser.add_argument(
        "--file",
        help="Process only a specific file (e.g., 4435.pdf)",
        default=None
    )
    ocr_parser.add_argument(
        "--summary",
        help="Print summary after processing",
        action="store_true"
    )
    
    # Parse command
    parse_parser = subparsers.add_parser("parse", help="Parse OCR text files to JSON")
    parse_parser.add_argument(
        "source",
        help="Source: either a directory with .txt files or a single .txt file"
    )
    parse_parser.add_argument(
        "--output-subdir",
        help="Optional subdirectory in invoices_json for output",
        default=None
    )
    
    # Process with parsing command
    process_parser = subparsers.add_parser("process", help="OCR + Parse in one step")
    process_parser.add_argument(
        "source_dir",
        help="Source directory containing PDF files to process"
    )
    process_parser.add_argument(
        "--output-dir",
        help="Optional custom output directory for text files",
        default=None
    )
    process_parser.add_argument(
        "--file",
        help="Process only a specific file",
        default=None
    )
    process_parser.add_argument(
        "--summary",
        help="Print summary after processing",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Handle OCR command
    if args.command == "ocr":
        handle_ocr_command(args)
    
    # Handle Parse command
    elif args.command == "parse":
        handle_parse_command(args)
    
    # Handle Process (OCR + Parse) command
    elif args.command == "process":
        handle_process_command(args)


def handle_ocr_command(args):
    """Handle OCR processing command."""
    # Resolve source directory path
    source_path = resolve_path(args.source_dir)
    
    # Validate source directory
    if not source_path.exists():
        print(f"Error: Directory not found: {args.source_dir}")
        print(f"Resolved path: {source_path}")
        print(f"Current working directory: {Path.cwd()}")
        sys.exit(1)
    
    if not source_path.is_dir():
        print(f"Error: Path is not a directory: {source_path}")
        sys.exit(1)
    
    try:
        # Resolve output directory if provided
        output_dir = None
        if args.output_dir:
            output_dir = str(resolve_path(args.output_dir))
        
        # Initialize processor
        processor = OCRProcessor(str(source_path), output_dir)
        
        print(f"Starting OCR processing...")
        print(f"Source: {source_path}")
        print(f"Output directory will be: {processor._get_output_directory()}\n")
        
        # Process files
        if args.file:
            # Process single file
            print(f"Processing single file: {args.file}\n")
            result = processor.process_single_file(args.file)
            print(json.dumps(result, indent=2))
        else:
            # Process entire directory
            print(f"Processing all PDF files in directory...\n")
            results = processor.process_directory()
            
            if args.summary:
                summary = processor.get_summary(results)
                print(f"\n{'='*50}")
                print("PROCESSING SUMMARY")
                print(f"{'='*50}")
                print(f"Total files processed: {summary['total_processed']}")
                print(f"Successful: {summary['successful']}")
                print(f"Failed: {summary['failed']}")
                print(f"Output directory: {summary['output_directory']}")
                
                if summary['failed_files']:
                    print(f"\nFailed files:")
                    for filename in summary['failed_files']:
                        print(f"  - {filename}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error during processing: {e}")
        sys.exit(1)


def handle_parse_command(args):
    """Handle data parsing command."""
    source_path = resolve_path(args.source)
    
    if not source_path.exists():
        print(f"Error: Path not found: {args.source}")
        sys.exit(1)
    
    try:
        parser_service = DataParserService()
        
        if source_path.is_file() and source_path.suffix == ".txt":
            # Parse single file
            print(f"Parsing single text file: {source_path.name}\n")
            result = parser_service.parse_txt_file(source_path, args.output_subdir)
            
            if result["status"] == "success":
                print(f"✓ Successfully parsed")
                print(f"  Input:  {result['source_file']}")
                print(f"  Output: {result['output_file']}")
                print(f"\nExtracted data:")
                print(json.dumps(result['data'], indent=2, ensure_ascii=False))
            else:
                print(f"✗ Error: {result['message']}")
        
        elif source_path.is_dir():
            # Parse all text files in directory
            print(f"Parsing all .txt files in: {source_path}\n")
            txt_files = sorted(source_path.glob("*.txt"))
            
            if not txt_files:
                print(f"No .txt files found in {source_path}")
                return
            
            results = []
            for txt_file in txt_files:
                result = parser_service.parse_txt_file(txt_file, args.output_subdir)
                results.append(result)
                
                status = "✓" if result["status"] == "success" else "✗"
                print(f"{status} {txt_file.name}")
            
            # Summary
            successful = [r for r in results if r["status"] == "success"]
            failed = [r for r in results if r["status"] == "error"]
            
            print(f"\n{'='*50}")
            print("PARSING SUMMARY")
            print(f"{'='*50}")
            print(f"Total files processed: {len(results)}")
            print(f"Successful: {len(successful)}")
            print(f"Failed: {len(failed)}")
            
            if failed:
                print(f"\nFailed files:")
                for result in failed:
                    print(f"  - {Path(result.get('source_file', 'unknown')).name}: {result.get('message')}")
        
        else:
            print(f"Error: Path must be a .txt file or directory")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error during parsing: {e}")
        sys.exit(1)


def handle_process_command(args):
    """Handle combined OCR + Parse command."""
    # Resolve source directory path
    source_path = resolve_path(args.source_dir)
    
    # Validate source directory
    if not source_path.exists():
        print(f"Error: Directory not found: {args.source_dir}")
        print(f"Resolved path: {source_path}")
        print(f"Current working directory: {Path.cwd()}")
        sys.exit(1)
    
    if not source_path.is_dir():
        print(f"Error: Path is not a directory: {source_path}")
        sys.exit(1)
    
    try:
        # Resolve output directory if provided
        output_dir = None
        if args.output_dir:
            output_dir = str(resolve_path(args.output_dir))
        
        # Initialize processor
        processor = OCRProcessor(str(source_path), output_dir)
        
        print(f"Starting OCR + PARSE processing...")
        print(f"Source: {source_path}")
        print(f"Text output: {processor._get_output_directory()}")
        print(f"JSON output: invoices_json/{processor._extract_year_from_path()}\n")
        
        # Process files
        if args.file:
            # Process single file
            print(f"Processing single file: {args.file}\n")
            result = processor.process_single_file_with_parsing(args.file)
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        else:
            # Process entire directory
            print(f"Processing all PDF files in directory...\n")
            results = processor.process_directory_with_parsing()
            
            if args.summary:
                # Calculate summary
                result_list = results.get("results", [])
                successful = [r for r in result_list if r["status"] == "success"]
                failed = [r for r in result_list if r["status"] == "error"]
                
                print(f"\n{'='*60}")
                print("PROCESSING SUMMARY (OCR + PARSE)")
                print(f"{'='*60}")
                print(f"Total files processed: {len(result_list)}")
                print(f"Successful: {len(successful)}")
                print(f"Failed: {len(failed)}")
                print(f"Text output directory: {results.get('output_directory')}")
                print(f"JSON output directory: {results.get('json_output_directory')}")
                
                if failed:
                    print(f"\nFailed files:")
                    for result in failed:
                        print(f"  - {result['filename']}: {result.get('message', 'Unknown error')}")
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error during processing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
