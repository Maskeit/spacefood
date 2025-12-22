"""
Standalone utility script for parsing OCR text files to JSON.
Useful for parsing existing .txt files without re-processing PDFs.
"""
import sys
import argparse
from pathlib import Path
from services.data_parser import DataParserService


def main():
    parser = argparse.ArgumentParser(
        description="Parse OCR text files to JSON invoice format"
    )
    
    parser.add_argument(
        "source",
        help="Source: either a directory with .txt files or a single .txt file"
    )
    
    parser.add_argument(
        "--output-subdir",
        help="Optional subdirectory in invoices_json for output",
        default=None
    )
    
    parser.add_argument(
        "--output-dir",
        help="Custom base directory for JSON output (defaults to invoices_json)",
        default=None
    )
    
    args = parser.parse_args()
    
    source_path = Path(args.source)
    
    if not source_path.exists():
        print(f"Error: Path not found: {args.source}")
        sys.exit(1)
    
    try:
        # Initialize parser service
        output_base = args.output_dir if args.output_dir else "invoices_json"
        parser_service = DataParserService(output_base_dir=output_base)
        
        if source_path.is_file() and source_path.suffix == ".txt":
            # Parse single file
            print(f"Parsing OCR text file: {source_path.name}\n")
            result = parser_service.parse_txt_file(source_path, args.output_subdir)
            
            if result["status"] == "success":
                print(f"✓ Successfully parsed")
                print(f"  Input:  {result['source_file']}")
                print(f"  Output: {result['output_file']}")
                print(f"\nExtracted data (JSON):")
                import json
                print(json.dumps(result['data'], indent=2, ensure_ascii=False))
            else:
                print(f"✗ Error: {result['message']}")
                sys.exit(1)
        
        elif source_path.is_dir():
            # Parse all text files in directory
            print(f"Parsing all .txt files in: {source_path}\n")
            txt_files = sorted(source_path.glob("*.txt"))
            
            if not txt_files:
                print(f"No .txt files found in {source_path}")
                sys.exit(1)
            
            print(f"Found {len(txt_files)} .txt files to process...\n")
            
            results = []
            for txt_file in txt_files:
                result = parser_service.parse_txt_file(txt_file, args.output_subdir)
                results.append(result)
                
                status = "✓" if result["status"] == "success" else "✗"
                output_name = Path(result.get('output_file', '')).name if result.get('output_file') else 'error'
                print(f"{status} {txt_file.name:<30} -> {output_name}")
            
            # Summary
            successful = [r for r in results if r["status"] == "success"]
            failed = [r for r in results if r["status"] == "error"]
            
            print(f"\n{'='*60}")
            print("PARSING SUMMARY")
            print(f"{'='*60}")
            print(f"Total files processed: {len(results)}")
            print(f"Successful: {len(successful)}")
            print(f"Failed: {len(failed)}")
            print(f"Output directory: {output_base}")
            if args.output_subdir:
                print(f"Output subdirectory: {args.output_subdir}")
            
            if failed:
                print(f"\nFailed files:")
                for result in failed:
                    source_name = Path(result.get('source_file', 'unknown')).name
                    print(f"  - {source_name}: {result.get('message')}")
            
            if failed:
                sys.exit(1)
        
        else:
            print(f"Error: Source must be a .txt file or directory containing .txt files")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error during parsing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
