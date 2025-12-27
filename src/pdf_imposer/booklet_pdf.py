"""Booklet PDF processing using pypdf."""

from pypdf import PageObject, PdfReader, PdfWriter

from .booklet import pad_page_order


def create_booklet_pdf(input_path: str, output_path: str) -> None:
    """
    Create a booklet-formatted PDF from an input PDF.

    This function:
    1. Reads the input PDF
    2. Pads the page count to a multiple of 4
    3. Reorders pages for booklet printing
    4. Writes the output PDF

    Args:
        input_path: Path to the input PDF file
        output_path: Path to save the booklet PDF
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()

    original_num_pages = len(reader.pages)

    # Get the booklet page order with padding
    page_order = pad_page_order(original_num_pages)

    # Create a blank page for padding (use first page size as reference)
    if original_num_pages > 0:
        first_page = reader.pages[0]
        blank_page = PageObject.create_blank_page(
            width=first_page.mediabox.width, height=first_page.mediabox.height
        )
    else:
        # Fallback to letter size if no pages
        blank_page = PageObject.create_blank_page(width=612, height=792)

    # Add pages in booklet order
    for page_idx in page_order:
        if page_idx is None:
            # Add blank page for padding
            writer.add_page(blank_page)
        else:
            # Add the actual page
            writer.add_page(reader.pages[page_idx])

    # Write the output
    with open(output_path, "wb") as output_file:
        writer.write(output_file)
