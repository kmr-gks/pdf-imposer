"""PDF cropping utilities using PyMuPDF."""

from typing import Tuple

import fitz  # PyMuPDF


def get_content_bbox(page: fitz.Page, margin: float = 0) -> Tuple[float, float, float, float]:
    """
    Get the bounding box of content on a page.

    Args:
        page: A PyMuPDF page object
        margin: Additional margin to add around the content (in points)

    Returns:
        A tuple (x0, y0, x1, y1) representing the bounding box
    """
    # Get all text and drawing blocks
    blocks = page.get_text("dict")["blocks"]
    drawings = page.get_drawings()

    if not blocks and not drawings:
        # No content found, return the full page
        return page.rect

    # Start with invalid bounds
    x0, y0 = float("inf"), float("inf")
    x1, y1 = float("-inf"), float("-inf")

    # Process text blocks
    for block in blocks:
        if "bbox" in block:
            bx0, by0, bx1, by1 = block["bbox"]
            x0 = min(x0, bx0)
            y0 = min(y0, by0)
            x1 = max(x1, bx1)
            y1 = max(y1, by1)

    # Process drawings
    for drawing in drawings:
        if "rect" in drawing:
            rect = drawing["rect"]
            x0 = min(x0, rect.x0)
            y0 = min(y0, rect.y0)
            x1 = max(x1, rect.x1)
            y1 = max(y1, rect.y1)

    # If still no bounds found, use page rect
    if x0 == float("inf"):
        return page.rect

    # Apply margin
    x0 = max(0, x0 - margin)
    y0 = max(0, y0 - margin)
    x1 = min(page.rect.width, x1 + margin)
    y1 = min(page.rect.height, y1 + margin)

    return (x0, y0, x1, y1)


def crop_pdf(input_path: str, output_path: str, margin: float = 10) -> None:
    """
    Crop a PDF to remove margins around content.

    Args:
        input_path: Path to the input PDF file
        output_path: Path to save the cropped PDF
        margin: Margin to preserve around content in points (default: 10)
    """
    doc = fitz.open(input_path)

    for page_num in range(len(doc)):
        page = doc[page_num]
        bbox = get_content_bbox(page, margin)
        page.set_cropbox(fitz.Rect(bbox))

    doc.save(output_path)
    doc.close()
