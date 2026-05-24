"""PyMuPDF implementation of PDFParser."""

import re
from pathlib import Path
from typing import List, Dict

import fitz  # PyMuPDF

from app.core.interfaces import PDFParser
from app.utils.config import config
from app.utils.exceptions import PDFParsingError, SectionNotFoundError
from app.utils.logger import logger


class PyMuPDFParser(PDFParser):
    """Extract sections from SLATEFALL dossier using PyMuPDF."""
    
    def __init__(self, pdf_path: Path = None):
        self.pdf_path = pdf_path or config.PDF_PATH
        self._section_cache: Dict[int, str] = {}
        self._available_sections: List[int] = []
        self._load_pdf()
    
    def _load_pdf(self) -> None:
        """Load PDF and extract sections."""
        if not self.pdf_path.exists():
            raise PDFParsingError(f"PDF file not found: {self.pdf_path}")
        
        try:
            doc = fitz.open(self.pdf_path)
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            doc.close()
            
            self._parse_sections(full_text)
            logger.info(f"Loaded PDF with sections: {self._available_sections}")
        except Exception as e:
            raise PDFParsingError(f"Failed to parse PDF: {e}")
    
    def _parse_sections(self, text: str) -> None:
        """Parse text to extract sections by number."""
        # Pattern for section headers like "Section 5." or "Section 5:"
        section_pattern = r"Section\s+(\d+)[\.:]"
        
        # Find all section headers with their positions
        matches = list(re.finditer(section_pattern, text))
        
        if not matches:
            raise PDFParsingError("No sections found in PDF")
        
        # Extract content between sections
        for i, match in enumerate(matches):
            section_num = int(match.group(1))
            start_pos = match.end()
            
            # End position is start of next section or end of text
            if i + 1 < len(matches):
                end_pos = matches[i + 1].start()
            else:
                end_pos = len(text)
            
            section_content = text[start_pos:end_pos].strip()
            
            # Clean up: remove page numbers and extra whitespace
            section_content = re.sub(r'\n\s*\n', '\n\n', section_content)
            section_content = re.sub(r'===== Page \d+ =====', '', section_content)
            
            self._section_cache[section_num] = section_content
            self._available_sections.append(section_num)
        
        logger.info(f"Parsed {len(self._section_cache)} sections")
    
    def extract_section(self, section_id: int) -> str:
        """Extract text content for a given section number."""
        if section_id not in self._section_cache:
            raise SectionNotFoundError(
                f"Section {section_id} not found. Available: {self._available_sections}"
            )
        return self._section_cache[section_id]
    
    def get_available_sections(self) -> List[int]:
        """Get list of available section numbers in the PDF."""
        return self._available_sections.copy()