"""PDF cropping utilities using PyMuPDF."""

from typing import Optional

import fitz  # PyMuPDF


def get_content_bbox(page: fitz.Page) -> Optional[fitz.Rect]:
    """Return the bounding box of visible content on a page.

    This inspects text blocks and vector drawings and returns the union rectangle.

    Returns:
        fitz.Rect if content is detected, otherwise None (e.g., blank page).
    """
    blocks = page.get_text("dict").get("blocks", [])
    drawings = page.get_drawings()

    if not blocks and not drawings:
        return None

    x0, y0 = float("inf"), float("inf")
    x1, y1 = float("-inf"), float("-inf")

    for block in blocks:
        bbox = block.get("bbox")
        if bbox:
            bx0, by0, bx1, by1 = bbox
            x0 = min(x0, bx0)
            y0 = min(y0, by0)
            x1 = max(x1, bx1)
            y1 = max(y1, by1)

    for drawing in drawings:
        rect = drawing.get("rect")
        if rect:
            x0 = min(x0, rect.x0)
            y0 = min(y0, rect.y0)
            x1 = max(x1, rect.x1)
            y1 = max(y1, rect.y1)

    if x0 == float("inf"):
        return None

    return fitz.Rect(x0, y0, x1, y1)


def crop_pdf(
    input_path: str, output_path: str, margin: float = 10, allow_upscale: bool = True
) -> None:
    """Reduce apparent margins by scaling the page content to fill the page.

    Instead of changing the crop box, this function creates a new PDF where each page's
    detected content area is placed into a target rectangle (page minus `margin`) while
    preserving aspect ratio. This effectively enlarges the content and reduces whitespace.

    Args:
        input_path: Path to the input PDF file.
        output_path: Path to save the processed PDF.
        margin: Margin to preserve around the scaled content in points (default: 10).
        allow_upscale: If False, content will not be enlarged beyond 100%.
    """
    src = fitz.open(input_path)
    dst = fitz.open()

    for page_num in range(len(src)):
        spage = src[page_num]
        page_rect = spage.rect

        # Target area inside the page where we want content to fit.
        target = fitz.Rect(
            margin,
            margin,
            max(margin, page_rect.width - margin),
            max(margin, page_rect.height - margin),
        )

        bbox = get_content_bbox(spage)

        # Create an output page with the same dimensions.
        dpage = dst.new_page(width=page_rect.width, height=page_rect.height)

        if bbox is None or bbox.is_empty:
            # Blank or undetectable content: copy the page as-is.
            dpage.show_pdf_page(page_rect, src, page_num)
            continue

        # Compute scale factor to fit bbox into target while preserving aspect ratio.
        bw, bh = bbox.width, bbox.height
        tw, th = target.width, target.height
        if bw <= 0 or bh <= 0 or tw <= 0 or th <= 0:
            dpage.show_pdf_page(page_rect, src, page_num)
            continue

        scale = min(tw / bw, th / bh)
        if not allow_upscale:
            scale = min(scale, 1.0)

        # Center the scaled content inside the target rect.
        out_w = bw * scale
        out_h = bh * scale
        x0 = target.x0 + (tw - out_w) / 2
        y0 = target.y0 + (th - out_h) / 2
        dest_rect = fitz.Rect(x0, y0, x0 + out_w, y0 + out_h)

        # Place the content area of the source page into dest_rect.
        # `clip=bbox` uses only the content area; scaling is achieved by mapping clip -> dest_rect.
        dpage.show_pdf_page(dest_rect, src, page_num, clip=bbox)

    dst.save(output_path)
    dst.close()
    src.close()
