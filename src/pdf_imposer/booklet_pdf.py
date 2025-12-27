"""Booklet PDF processing using pypdf."""

from __future__ import annotations
from typing import Optional, Tuple
from pypdf import PageObject, PdfReader, PdfWriter, Transformation
from .booklet import pad_page_order


def _get_page_or_blank(
    reader: PdfReader, idx: Optional[int], blank_page: PageObject
) -> PageObject:
    if idx is None:
        return blank_page
    return reader.pages[idx]


def _landscape_sheet_size(first_page: PageObject) -> Tuple[float, float]:
    # Use the first page size as reference; output as landscape of that size.
    w = float(first_page.mediabox.width)
    h = float(first_page.mediabox.height)
    return (max(w, h), min(w, h))


def _place_page_into_slot(
    sheet: PageObject,
    src_page: PageObject,
    slot_x0: float,
    slot_y0: float,
    slot_w: float,
    slot_h: float,
) -> None:
    # Scale src page to fit inside the slot while preserving aspect ratio, then center it.
    pw = float(src_page.mediabox.width)
    ph = float(src_page.mediabox.height)

    if pw <= 0 or ph <= 0 or slot_w <= 0 or slot_h <= 0:
        return

    s = min(slot_w / pw, slot_h / ph)
    out_w = pw * s
    out_h = ph * s

    tx = slot_x0 + (slot_w - out_w) / 2.0
    ty = slot_y0 + (slot_h - out_h) / 2.0

    t = Transformation().scale(sx=s, sy=s).translate(tx=tx, ty=ty)
    sheet.merge_transformed_page(src_page, t)


def create_booklet_pdf(input_path: str, output_path: str) -> None:
    """
    Create a booklet-imposed PDF (2-up) from an input PDF.

    Output:
    - Each output page is a "sheet side" (landscape) containing 2 logical pages (left/right).
    - The order is suitable for double-sided printing and folding into a booklet.
    - Page count is padded to a multiple of 4 with blank pages as needed.
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()

    original_num_pages = len(reader.pages)

    if original_num_pages == 0:
        # Create an empty PDF output
        with open(output_path, "wb") as f:
            writer.write(f)
        return

    # Padding + booklet order (0-based indices) with None for blanks.
    # The returned order is grouped per sheet as:
    # [right_front, left_front, left_back, right_back] repeated.
    page_order = pad_page_order(original_num_pages)

    first_page = reader.pages[0]
    blank_page = PageObject.create_blank_page(
        width=first_page.mediabox.width, height=first_page.mediabox.height
    )

    sheet_w, sheet_h = _landscape_sheet_size(first_page)

    # Each output page (sheet side) holds two slots: left and right.
    slot_w = sheet_w / 2.0
    slot_h = sheet_h

    # Process 4 items per physical sheet: RF, LF, LB, RB
    if len(page_order) % 4 != 0:
        raise ValueError("Internal error: booklet order length must be multiple of 4")
    
    for i in range(0, len(page_order), 4):
        lf, rf, lb, rb = page_order[i : i + 4]
    
        # FRONT side: (left=lf, right=rf)
        front = PageObject.create_blank_page(width=sheet_w, height=sheet_h)
        _place_page_into_slot(
            front,
            _get_page_or_blank(reader, lf, blank_page),
            slot_x0=0.0,
            slot_y0=0.0,
            slot_w=slot_w,
            slot_h=slot_h,
        )
        _place_page_into_slot(
            front,
            _get_page_or_blank(reader, rf, blank_page),
            slot_x0=slot_w,
            slot_y0=0.0,
            slot_w=slot_w,
            slot_h=slot_h,
        )
        writer.add_page(front)
    
        # BACK side: (left=lb, right=rb)
        back = PageObject.create_blank_page(width=sheet_w, height=sheet_h)
        _place_page_into_slot(
            back,
            _get_page_or_blank(reader, lb, blank_page),
            slot_x0=0.0,
            slot_y0=0.0,
            slot_w=slot_w,
            slot_h=slot_h,
        )
        _place_page_into_slot(
            back,
            _get_page_or_blank(reader, rb, blank_page),
            slot_x0=slot_w,
            slot_y0=0.0,
            slot_w=slot_w,
            slot_h=slot_h,
        )
        writer.add_page(back)

    with open(output_path, "wb") as output_file:
        writer.write(output_file)