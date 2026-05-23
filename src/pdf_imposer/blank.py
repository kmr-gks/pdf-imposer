"""Insert blank pages into PDF files."""

import fitz  # PyMuPDF


def insert_blank_pages(
    input_path: str,
    output_path: str,
    keep_first_page: bool = True,
) -> None:
    """
    Insert blank pages before all pages except the first page.

    Example:
        [1,2,3] -> [1,blank,2,blank,3]

    Args:
        input_path: Input PDF path
        output_path: Output PDF path
        keep_first_page:
            If True, the first page is kept without a preceding blank page.
    """
    src = fitz.open(input_path)
    dst = fitz.open()

    if src.page_count == 0:
        dst.save(output_path)
        dst.close()
        src.close()
        return

    for i in range(src.page_count):
        src_page = src[i]
        rect = src_page.rect

        # Insert blank page before non-first pages
        if not (keep_first_page and i == 0):
            dst.new_page(width=rect.width, height=rect.height)

        # Copy original page
        new_page = dst.new_page(width=rect.width, height=rect.height)
        new_page.show_pdf_page(rect, src, i)

    dst.save(output_path)
    dst.close()
    src.close()
