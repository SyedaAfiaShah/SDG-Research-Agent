import os
import re

def get_doc_type(filename: str) -> str:
    """
    Determines the document type (category) from the filename.
    Matches standard patterns:
    - HDR_... -> hdr
    - ITU_... -> itu
    - SDG_... -> sdg
    - WorldBank_... -> worldbank
    Defaults to 'other' if unknown.
    """
    filename_lower = os.path.basename(filename).lower()
    if "hdr" in filename_lower:
        return "hdr"
    elif "itu" in filename_lower:
        return "itu"
    elif "sdg" in filename_lower:
        return "sdg"
    elif "worldbank" in filename_lower or "world_bank" in filename_lower:
        return "worldbank"
    else:
        return "other"

def clean_text(text: str) -> str:
    """
    Applies basic text cleaning to extracted PDF contents:
    - Normalizes spacing and removes consecutive newlines/spaces
    - Cleans up weird control characters
    """
    if not text:
        return ""
    # Replace multiple newlines or whitespaces with a single space
    text = re.sub(r'\s+', ' ', text)
    # Remove null bytes or other control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
    return text.strip()
