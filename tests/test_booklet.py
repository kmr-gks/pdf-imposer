"""Tests for booklet page ordering functions."""

import pytest

from pdf_imposer.booklet import (
    calculate_booklet_pages,
    generate_booklet_order,
    pad_page_order,
)


class TestCalculateBookletPages:
    """Tests for calculate_booklet_pages function."""

    def test_multiple_of_4(self):
        """Test that multiples of 4 are unchanged."""
        assert calculate_booklet_pages(4) == 4
        assert calculate_booklet_pages(8) == 8
        assert calculate_booklet_pages(12) == 12
        assert calculate_booklet_pages(100) == 100

    def test_padding_needed(self):
        """Test that non-multiples are padded to next multiple of 4."""
        assert calculate_booklet_pages(1) == 4
        assert calculate_booklet_pages(2) == 4
        assert calculate_booklet_pages(3) == 4
        assert calculate_booklet_pages(5) == 8
        assert calculate_booklet_pages(6) == 8
        assert calculate_booklet_pages(7) == 8
        assert calculate_booklet_pages(9) == 12
        assert calculate_booklet_pages(10) == 12

    def test_zero_pages(self):
        """Test that zero pages returns zero."""
        assert calculate_booklet_pages(0) == 0


class TestGenerateBookletOrder:
    """Tests for generate_booklet_order function."""

    def test_4_pages(self):
        """Test booklet order for 4 pages."""
        # For 4 pages, order should be: [3, 0, 1, 2]
        # Sheet front: page 4 (idx 3), page 1 (idx 0)
        # Sheet back: page 2 (idx 1), page 3 (idx 2)
        order = generate_booklet_order(4)
        assert order == [3, 0, 1, 2]

    def test_8_pages(self):
        """Test booklet order for 8 pages."""
        # For 8 pages:
        # Sheet 1 front: page 8 (idx 7), page 1 (idx 0)
        # Sheet 1 back: page 2 (idx 1), page 7 (idx 6)
        # Sheet 2 front: page 6 (idx 5), page 3 (idx 2)
        # Sheet 2 back: page 4 (idx 3), page 5 (idx 4)
        order = generate_booklet_order(8)
        assert order == [7, 0, 1, 6, 5, 2, 3, 4]

    def test_12_pages(self):
        """Test booklet order for 12 pages."""
        order = generate_booklet_order(12)
        # 3 sheets needed
        assert len(order) == 12
        # Sheet 1: [11, 0, 1, 10]
        # Sheet 2: [9, 2, 3, 8]
        # Sheet 3: [7, 4, 5, 6]
        assert order == [11, 0, 1, 10, 9, 2, 3, 8, 7, 4, 5, 6]

    def test_invalid_not_multiple_of_4(self):
        """Test that non-multiples of 4 raise ValueError."""
        with pytest.raises(ValueError, match="must be multiple of 4"):
            generate_booklet_order(3)
        with pytest.raises(ValueError, match="must be multiple of 4"):
            generate_booklet_order(5)
        with pytest.raises(ValueError, match="must be multiple of 4"):
            generate_booklet_order(10)

    def test_all_indices_used(self):
        """Test that all page indices appear exactly once."""
        for num_pages in [4, 8, 12, 16, 20]:
            order = generate_booklet_order(num_pages)
            assert sorted(order) == list(range(num_pages))

    def test_length_matches(self):
        """Test that output length matches input."""
        for num_pages in [4, 8, 12, 16, 20, 100]:
            order = generate_booklet_order(num_pages)
            assert len(order) == num_pages


class TestPadPageOrder:
    """Tests for pad_page_order function."""

    def test_no_padding_needed(self):
        """Test when original pages are already multiple of 4."""
        order = pad_page_order(4)
        assert None not in order
        assert len(order) == 4
        assert order == [3, 0, 1, 2]

    def test_one_blank_page(self):
        """Test with 3 pages needing 1 blank."""
        order = pad_page_order(3)
        assert len(order) == 4
        # Last page (idx 3) should be None (blank)
        assert order.count(None) == 1
        assert order == [None, 0, 1, 2]

    def test_two_blank_pages(self):
        """Test with 2 pages needing 2 blanks."""
        order = pad_page_order(2)
        assert len(order) == 4
        assert order.count(None) == 2
        # Pages 2 and 3 (indices 2 and 3) should be None
        assert order == [None, 0, 1, None]

    def test_three_blank_pages(self):
        """Test with 1 page needing 3 blanks."""
        order = pad_page_order(1)
        assert len(order) == 4
        assert order.count(None) == 3
        # Only page 1 (idx 0) exists, rest are blank
        assert order == [None, 0, None, None]

    def test_5_pages(self):
        """Test with 5 pages needing 3 blanks to reach 8."""
        order = pad_page_order(5)
        assert len(order) == 8
        assert order.count(None) == 3
        # Pages 6, 7, 8 (indices 5, 6, 7) should be None
        expected = [None, 0, 1, None, None, 2, 3, 4]
        assert order == expected

    def test_valid_page_indices(self):
        """Test that non-None values are valid page indices."""
        for original_pages in [1, 2, 3, 5, 6, 7, 9, 10, 11]:
            order = pad_page_order(original_pages)
            for idx in order:
                if idx is not None:
                    assert 0 <= idx < original_pages

    def test_all_original_pages_present(self):
        """Test that all original page indices appear in the order."""
        for original_pages in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            order = pad_page_order(original_pages)
            non_none_indices = [idx for idx in order if idx is not None]
            assert sorted(non_none_indices) == list(range(original_pages))
