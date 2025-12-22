"""
Data Parser Service for extracting structured data from OCR text.
Converts raw OCR text to JSON format based on predefined schema.
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataParser:
    """
    Parser service that extracts structured data from OCR text.
    Converts raw OCR output to JSON format matching the invoice schema.
    """

    # Define the schema structure
    SCHEMA = {
        "importador": {
            "nombre": "importador_nombre",
            "domicilio": "importador_domicilio",
            "rfc": "importador_rfc"
        },
        "pedimento": {
            "numero": "pedimento",
            "fecha": "fecha_pedimento"
        },
        "factura": {
            "numero": "num_factura",
            "fecha": "fecha_factura",
            "lugar": "lugar_em_factura"
        }
    }

    def __init__(self, ocr_text: str):
        """
        Initialize the parser with OCR text.

        Args:
            ocr_text: Raw text extracted from OCR
        """
        self.ocr_text = ocr_text.lower()  # Convert to lowercase for easier matching
        self.original_text = ocr_text  # Keep original for reference
        self.data = {}

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean extracted text by removing extra whitespace."""
        return re.sub(r'\s+', ' ', text.strip())

    def _extract_field(self, keywords: List[str], context_lines: int = 2) -> Optional[str]:
        """
        Extract a field value by searching for keywords.

        Args:
            keywords: List of keywords to search for
            context_lines: Number of lines after keyword to search for value

        Returns:
            Extracted value or None
        """
        lines = self.ocr_text.split('\n')

        for i, line in enumerate(lines):
            for keyword in keywords:
                if keyword.lower() in line:
                    # Try to extract value from the same line or following lines
                    for j in range(i, min(i + context_lines + 1, len(lines))):
                        candidate = lines[j].strip()
                        if candidate and candidate != line.strip():
                            return self._clean_text(candidate)
                    # If found keyword, try to extract from after the keyword
                    value = line.split(keyword.lower())[-1].strip()
                    if value:
                        return self._clean_text(value)
        return ""

    def _extract_importador(self) -> Dict[str, str]:
        """Extract importer/importador information."""
        return {
            "importador_nombre": self._extract_field([
                "importador", "empresa", "razón social", "razon social"
            ]),
            "importador_domicilio": self._extract_field([
                "domicilio", "dirección", "direccion", "domicilio del importador"
            ]),
            "importador_rfc": self._extract_field([
                "rfc", "registro federal", "clave de rfc"
            ])
        }

    def _extract_pedimento(self) -> Dict[str, str]:
        """Extract pedimento (customs document) information."""
        return {
            "pedimento": self._extract_field([
                "pedimento", "número de pedimento", "numero de pedimento",
                "aduana pedimento"
            ]),
            "fecha_pedimento": self._extract_field([
                "fecha pedimento", "fecha de pedimento"
            ])
        }

    def _extract_factura(self) -> Dict[str, str]:
        """Extract invoice information."""
        return {
            "num_factura": self._extract_field([
                "factura", "número de factura", "numero de factura",
                "folio factura", "invoice"
            ]),
            "fecha_factura": self._extract_field([
                "fecha factura", "fecha de factura", "fecha emisión"
            ]),
            "lugar_em_factura": self._extract_field([
                "lugar", "lugar de emisión", "lugar de emision"
            ])
        }

    def _extract_proveedores(self) -> List[Dict[str, str]]:
        """Extract supplier/proveedor information."""
        proveedores = []

        # Search for supplier section
        supplier_keywords = ["proveedor", "supplier", "vendedor", "exportador"]
        lines = self.original_text.split('\n')

        supplier_section = []
        in_supplier_section = False

        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in supplier_keywords):
                in_supplier_section = True

            if in_supplier_section:
                supplier_section.append(line)
                # End supplier section after collecting enough lines
                if len(supplier_section) > 10:
                    break

        supplier_text = '\n'.join(supplier_section).lower()

        proveedor = {
            "id_fiscal": self._extract_field_from_text(supplier_text, [
                "id fiscal", "idn", "tax id", "rfc"
            ]) or "",
            "nombre": self._extract_field_from_text(supplier_text, [
                "nombre", "company", "empresa"
            ]) or "",
            "domicilio": self._extract_field_from_text(supplier_text, [
                "domicilio", "dirección", "direccion", "address"
            ]) or ""
        }

        if any(proveedor.values()):
            proveedores.append(proveedor)

        return proveedores

    def _extract_field_from_text(self, text: str, keywords: List[str]) -> Optional[str]:
        """Helper to extract field from specific text block."""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            for keyword in keywords:
                if keyword.lower() in line:
                    value = line.split(keyword.lower())[-1].strip()
                    if value:
                        return self._clean_text(value)
                    # Try next line
                    if i + 1 < len(lines):
                        return self._clean_text(lines[i + 1].strip())
        return ""

    def _extract_partidas(self) -> List[Dict[str, str]]:
        """Extract product line items (partidas)."""
        partidas = []

        # Search for partida/item section
        partida_keywords = ["partida", "item", "producto", "descripción"]
        lines = self.original_text.split('\n')

        partida_section = []
        in_partida_section = False

        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in partida_keywords):
                in_partida_section = True

            if in_partida_section:
                partida_section.append(line)

        partida_text = '\n'.join(partida_section).lower()

        # Try to extract multiple partidas
        partida = {
            "partida": self._extract_field_from_text(partida_text, ["partida", "item #"]) or "",
            "secuencia": self._extract_field_from_text(partida_text, ["secuencia", "sequence"]) or "",
            "valor_aduana": self._extract_field_from_text(partida_text, ["valor aduana", "valor", "price"]) or "",
            "fraccion": self._extract_field_from_text(partida_text, ["fracción", "fraccion", "tariff"]) or "",
            "descripcion": self._extract_field_from_text(partida_text, ["descripción", "descripcion", "description"]) or "",
            "cantidad_umc": self._extract_field_from_text(partida_text, ["cantidad", "qty", "umc"]) or "",
            "pais_produccion": self._extract_field_from_text(partida_text, ["país producción", "pais produccion", "country of origin"]) or "",
            "pais_procedencia": self._extract_field_from_text(partida_text, ["país procedencia", "pais procedencia", "country"]) or "",
            "precio_pagado": self._extract_field_from_text(partida_text, ["precio pagado", "paid price"]) or "",
            "precio_unitario": self._extract_field_from_text(partida_text, ["precio unitario", "unit price"]) or ""
        }

        if any(partida.values()):
            partidas.append(partida)

        return partidas

    def parse(self) -> Dict[str, Any]:
        """
        Parse the OCR text and return structured JSON data.

        Returns:
            Dictionary with extracted data matching the schema
        """
        result = {}

        # Extract importador
        importador = self._extract_importador()
        result["importador_nombre"] = importador.get("importador_nombre", "")
        result["importador_domicilio"] = importador.get("importador_domicilio", "")
        result["importador_rfc"] = importador.get("importador_rfc", "")

        # Extract pedimento
        pedimento = self._extract_pedimento()
        result["pedimento"] = pedimento.get("pedimento", "")
        result["fecha_pedimento"] = pedimento.get("fecha_pedimento", "")

        # Extract factura
        factura = self._extract_factura()
        result["num_factura"] = factura.get("num_factura", "")
        result["fecha_factura"] = factura.get("fecha_factura", "")
        result["lugar_em_factura"] = factura.get("lugar_em_factura", "")

        # Extract proveedores
        result["proveedores"] = self._extract_proveedores()

        # Extract partidas
        result["partidas"] = self._extract_partidas()

        self.data = result
        return result

    def to_json(self, pretty: bool = True) -> str:
        """
        Convert parsed data to JSON string.

        Args:
            pretty: Whether to format JSON with indentation

        Returns:
            JSON string representation of parsed data
        """
        if not self.data:
            self.parse()

        if pretty:
            return json.dumps(self.data, indent=2, ensure_ascii=False)
        return json.dumps(self.data, ensure_ascii=False)

    @staticmethod
    def from_txt_file(txt_path: Path) -> 'DataParser':
        """
        Create a DataParser instance from a text file.

        Args:
            txt_path: Path to the OCR text file

        Returns:
            DataParser instance
        """
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return DataParser(text)


class DataParserService:
    """Service for managing data parsing operations."""

    def __init__(self, output_base_dir: str = "invoices_json"):
        """
        Initialize the parser service.

        Args:
            output_base_dir: Base directory for saving JSON results
        """
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(parents=True, exist_ok=True)

    def parse_txt_file(self, txt_path: Path, output_subdir: str = None) -> Dict[str, str]:
        """
        Parse a text file and save the result as JSON.

        Args:
            txt_path: Path to the OCR text file
            output_subdir: Optional subdirectory for the output

        Returns:
            Dictionary with status and file paths
        """
        if not txt_path.exists():
            return {
                "status": "error",
                "message": f"Text file not found: {txt_path}"
            }

        try:
            # Parse the text file
            parser = DataParser.from_txt_file(txt_path)
            parsed_data = parser.parse()

            # Determine output directory
            if output_subdir:
                output_dir = self.output_base_dir / output_subdir
            else:
                # Extract year from txt_path if possible
                year = self._extract_year_from_path(txt_path)
                output_dir = self.output_base_dir / year

            output_dir.mkdir(parents=True, exist_ok=True)

            # Create output filename
            filename = txt_path.stem
            output_path = output_dir / f"{filename}.json"

            # Save JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(parser.to_json(pretty=True))

            return {
                "status": "success",
                "source_file": str(txt_path),
                "output_file": str(output_path),
                "data": parsed_data
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error parsing {txt_path.name}: {str(e)}"
            }

    def parse_from_text(self, text: str, output_filename: str, output_subdir: str = None) -> Dict[str, str]:
        """
        Parse raw OCR text and save the result as JSON.

        Args:
            text: Raw OCR text
            output_filename: Name for the output JSON file (without extension)
            output_subdir: Optional subdirectory for the output

        Returns:
            Dictionary with status and file paths
        """
        try:
            # Parse the text
            parser = DataParser(text)
            parsed_data = parser.parse()

            # Determine output directory
            if output_subdir:
                output_dir = self.output_base_dir / output_subdir
            else:
                output_dir = self.output_base_dir

            output_dir.mkdir(parents=True, exist_ok=True)

            # Save JSON
            output_path = output_dir / f"{output_filename}.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(parser.to_json(pretty=True))

            return {
                "status": "success",
                "output_file": str(output_path),
                "data": parsed_data
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error parsing text: {str(e)}"
            }

    @staticmethod
    def _extract_year_from_path(path: Path) -> str:
        """Extract year from file path."""
        parts = path.parts
        for part in parts:
            if part.isdigit() and len(part) == 4 and 2000 <= int(part) <= 2100:
                return part
        return "unknown"
