"""Booklet printing utilities for PDF files."""

from typing import List, Optional


def calculate_booklet_pages(num_pages: int) -> int:
    """
    Calculate the number of pages needed for booklet printing.

    Booklet printing requires the total number of pages to be a multiple of 4.

    Args:
        num_pages: The current number of pages in the document

    Returns:
        The total number of pages needed (multiple of 4)
    """
    if num_pages % 4 == 0:
        return num_pages
    return ((num_pages // 4) + 1) * 4


def generate_booklet_order(num_pages: int) -> List[int]:
    """
    Generate the page order for booklet printing.

    For booklet printing, pages are arranged in a specific order so that when
    printed double-sided and folded, they appear in the correct sequence.

    The order follows this pattern for each sheet (4 pages):
    - Front: [last, first]
    - Back: [first+1, last-1]

    Args:
        num_pages: The total number of pages (must be multiple of 4)

    Returns:
        A list of page indices (0-based) in the order they should appear in the booklet.

    Raises:
        ValueError: If num_pages is not a multiple of 4
    """
    if num_pages % 4 != 0:
        raise ValueError(f"Number of pages must be multiple of 4, got {num_pages}")

    order = []
    sheets = num_pages // 4

    for sheet in range(sheets):
        # Each sheet has 4 pages: 2 on front, 2 on back
        # Front of sheet: right page is from end, left page is from start
        # Back of sheet: left page continues from start, right page continues from end

        start_idx = sheet * 2
        end_idx = num_pages - 1 - (sheet * 2)

        # Front of sheet (right to left when looking at spread)
        order.append(end_idx)  # Right page of front
        order.append(start_idx)  # Left page of front

        # Back of sheet (left to right when looking at spread)
        order.append(start_idx + 1)  # Left page of back
        order.append(end_idx - 1)  # Right page of back

    return order


def pad_page_order(original_num_pages: int) -> List[Optional[int]]:
    """
    Generate page order with padding for booklet printing.

    This function combines padding and reordering. It determines how many pages
    are needed, then generates the correct order, using None for blank pages.

    Args:
        original_num_pages: The original number of pages in the document

    Returns:
        A list of page indices (0-based) in booklet order, with None for blank pages
    """
    padded_num_pages = calculate_booklet_pages(original_num_pages)
    booklet_order = generate_booklet_order(padded_num_pages)

    # Replace page indices beyond the original count with None (blank pages)
    return [idx if idx < original_num_pages else None for idx in booklet_order]
