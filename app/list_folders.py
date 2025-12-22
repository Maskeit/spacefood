"""
Utility script to list available data directories.
Helps identify which folders contain PDF files.
"""
import sys
from pathlib import Path


def list_available_folders(base_path: str = "/Users/alejandre/Developer/jatenx/spacefood/app/data"):
    """
    List all year folders and the number of PDFs in each.
    """
    base = Path(base_path)
    
    if not base.exists():
        print(f"Error: Base directory not found: {base_path}")
        return
    
    print(f"Available data folders in: {base}\n")
    print(f"{'Year':<10} {'PDF Count':<15} {'Folder Path':<60}")
    print("=" * 85)
    
    year_folders = sorted([d for d in base.iterdir() if d.is_dir()])
    
    if not year_folders:
        print("No year folders found!")
        return
    
    for folder in year_folders:
        pdf_count = len(list(folder.glob("*.pdf")))
        print(f"{folder.name:<10} {pdf_count:<15} {str(folder):<60}")
    
    print("\n" + "=" * 85)
    print("Usage example:")
    print("  python3 main.py /Users/alejandre/Developer/jatenx/spacefood/app/data/2020 --summary")
    print("  python3 main.py /Users/alejandre/Developer/jatenx/spacefood/app/data/2021 --summary")


if __name__ == "__main__":
    base_path = "/Users/alejandre/Developer/jatenx/spacefood/app/data"
    
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    
    list_available_folders(base_path)
