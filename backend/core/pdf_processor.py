"""PDF processor - extract text from PDFs using pdfplumber and PyMuPDF"""
import os
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Process PDF files for text extraction"""
    
    SUPPORTED_EXTENSIONS = ('.pdf',)
    
    @staticmethod
    def extract_text(file_path: str) -> tuple:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            tuple: (text_content, error_message)
        """
        try:
            if not os.path.exists(file_path):
                return None, "File does not exist"
            
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return None, "File is empty"
            
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in PDFProcessor.SUPPORTED_EXTENSIONS:
                return None, f"Not a PDF file: {ext}"
            
            logger.info(f"Extracting text from: {file_path} ({file_size} bytes)")
            
            # Try pdfplumber first (better for structured content)
            try:
                import pdfplumber
                text = ""
                with pdfplumber.open(file_path) as pdf:
                    for page_num, page in enumerate(pdf.pages, 1):
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\n--- Page {page_num} ---\n{page_text}"
                
                if text.strip():
                    logger.info(f"Extracted {len(text)} chars using pdfplumber")
                    return text, None
                else:
                    logger.warning("pdfplumber returned empty text")
            
            except Exception as e:
                logger.warning(f"pdfplumber failed: {e}")
            
            # Fallback to PyMuPDF
            try:
                import fitz
                text = ""
                doc = fitz.open(file_path)
                for page_num, page in enumerate(doc, 1):
                    page_text = page.get_text()
                    if page_text:
                        text += f"\n--- Page {page_num} ---\n{page_text}"
                
                if text.strip():
                    logger.info(f"Extracted {len(text)} chars using PyMuPDF")
                    return text, None
            
            except Exception as e:
                logger.warning(f"PyMuPDF failed: {e}")
            
            return None, "Could not extract text from PDF"
        
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return None, str(e)
    
    @staticmethod
    def search_content(file_path: str, keywords: List[str], case_sensitive: bool = False) -> List[Dict]:
        """
        Search for keywords in PDF content
        
        Args:
            file_path: Path to PDF file
            keywords: Keywords to search for
            case_sensitive: Case-sensitive search
            
        Returns:
            List of matches with page numbers
        """
        results = []
        
        text, error = PDFProcessor.extract_text(file_path)
        if error:
            return [{"error": error, "file_path": file_path}]
        
        if not text:
            return []
        
        # Search by page
        pages = text.split("--- Page ")
        for page_num, page_text in enumerate(pages[1:], 1):
            for keyword in keywords:
                search_term = keyword if case_sensitive else keyword.lower()
                check_text = page_text if case_sensitive else page_text.lower()
                
                if search_term in check_text:
                    # Get context (50 chars before and after)
                    idx = check_text.find(search_term)
                    start = max(0, idx - 50)
                    end = min(len(page_text), idx + len(search_term) + 50)
                    context = page_text[start:end].replace("\n", " ")
                    
                    results.append({
                        "keyword": keyword,
                        "page": page_num,
                        "context": f"...{context}...",
                        "file_path": file_path
                    })
        
        return results
