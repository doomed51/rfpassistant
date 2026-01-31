"""Utility module for handling PDF files."""

import base64
from io import BytesIO
from typing import Tuple
import PyPDF2


def pdf_to_base64(uploaded_file) -> Tuple[str, int]:
    """
    Convert uploaded PDF to base64 for Claude API.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    
    Returns:
        Tuple of (base64_string, page_count)
    
    Raises:
        Exception: If PDF cannot be read or converted
    """
    try:
        # Read the uploaded file
        pdf_bytes = uploaded_file.read()
        
        # Get page count
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        page_count = len(pdf_reader.pages)
        
        # Convert to base64
        base64_pdf = base64.standard_b64encode(pdf_bytes).decode('utf-8')
        
        # Reset file pointer for potential reuse
        uploaded_file.seek(0)
        
        return base64_pdf, page_count
    
    except Exception as e:
        raise Exception(f"Failed to process PDF: {str(e)}")


def validate_pdf(uploaded_file) -> Tuple[bool, str]:
    """
    Validate that file is a readable PDF.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        page_count = len(pdf_reader.pages)
        
        # Reset file pointer
        uploaded_file.seek(0)
        
        if page_count == 0:
            return False, "PDF appears to be empty (0 pages)"
        
        return True, ""
    
    except PyPDF2.errors.PdfReadError:
        return False, "File is not a valid PDF or is corrupted"
    except Exception as e:
        return False, f"Error reading PDF: {str(e)}"


def get_pdf_info(uploaded_file) -> dict:
    """
    Extract basic information from PDF.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    
    Returns:
        Dictionary with PDF information (pages, size, name)
    """
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        uploaded_file.seek(0)
        
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        
        return {
            "name": uploaded_file.name,
            "pages": len(pdf_reader.pages),
            "size_mb": round(file_size_mb, 2)
        }
    
    except Exception as e:
        return {
            "name": uploaded_file.name,
            "pages": 0,
            "size_mb": 0,
            "error": str(e)
        }
