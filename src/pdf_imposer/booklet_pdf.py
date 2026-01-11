"""Booklet PDF processing (2-up) using PyMuPDF."""

from __future__ import annotations

from typing import Optional

import fitz  # PyMuPDF

from .booklet import pad_page_order


def create_booklet_pdf(input_path: str, output_path: str) -> None:
    """
    Create a booklet-imposed PDF (2-up) from an input PDF.

    - Each output page is a sheet side (landscape) containing two logical pages.
    - Page order is suitable for double-sided printing and folding into a booklet.
    - Pages are padded to a multiple of 4 with blanks as needed.

    NOTE:
    - We use PyMuPDF's show_pdf_page() to preserve visual fidelity (fonts/symbols),
      avoiding font/resource issues that can occur with pypdf merging.
    """
    src = fitz.open(input_path)
    if src.page_count == 0:
        fitz.open().save(output_path)
        src.close()
        return

    order = pad_page_order(src.page_count)  # [lf, rf, lb, rb] ... with None

    first = src[0]
    in_rect = first.rect  # original page size

    # Output sheet: landscape based on original page size
    sheet_w = max(in_rect.width, in_rect.height)
    sheet_h = min(in_rect.width, in_rect.height)

    left_rect = fitz.Rect(0, 0, sheet_w / 2, sheet_h)
    right_rect = fitz.Rect(sheet_w / 2, 0, sheet_w, sheet_h)

    dst = fitz.open()

    def show(target_page: fitz.Page, rect: fitz.Rect, idx: Optional[int]) -> None:
        if idx is None:
            return
        # IMPORTANT: no clip -> keep everything (prevents losing numbers near margins)
        sp = src[idx]
        pix = sp.get_pixmap(dpi=450, alpha=False)
        target_page.insert_image(rect, pixmap=pix)

    if len(order) % 4 != 0:
        src.close()
        raise ValueError("Internal error: booklet order length must be multiple of 4")

    for i in range(0, len(order), 4):
        lf, rf, lb, rb = order[i : i + 4]

        # FRONT side
        p = dst.new_page(width=sheet_w, height=sheet_h)
        show(p, left_rect, lf)
        show(p, right_rect, rf)

        # BACK side
        p = dst.new_page(width=sheet_w, height=sheet_h)
        show(p, left_rect, lb)
        show(p, right_rect, rb)

    dst.save(output_path)
    dst.close()
    src.close()
