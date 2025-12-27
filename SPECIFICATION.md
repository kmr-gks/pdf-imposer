
# CLI Specification — pdf-imposer

This document defines the command-line interface behavior for `pdf-imposer`, aligned with the README.

---

## 1. Command Name

- `pdf-imposer`

The CLI may also be invoked as:

```bash
python -m pdf_imposer.cli
```

---

## 2. Global Behavior

### 2.1 Help

- `pdf-imposer --help` shows top-level help.
- `pdf-imposer <command> --help` shows command-specific help.

### 2.2 Exit Codes

- `0`: Success
- `1`: General failure
- `2`: Invalid usage or arguments

---

## 3. Commands

### 3.1 crop

Reduce margins by auto-detecting content boundaries.

```bash
pdf-imposer crop INPUT OUTPUT [--margin PT]
```

- `INPUT`: input PDF file
- `OUTPUT`: output PDF file
- `--margin PT`: margin to keep around content (default defined by implementation)

Behavior:
- Detect content bounding boxes using PyMuPDF
- Reduce margins around detected content
- Write a new PDF

---

### 3.2 booklet

Reorder pages for booklet-style printing.

```bash
pdf-imposer booklet INPUT OUTPUT
```

Behavior:
- Pad page count to a multiple of 4 if needed
- Reorder pages so double-sided printing and folding produces correct reading order

Example for 4 pages:
- Front: pages 4 and 1
- Back: pages 2 and 3

---

### 3.3 auto

Run the full processing pipeline.

```bash
pdf-imposer auto INPUT OUTPUT [--margin PT]
```

Behavior:
- Run `crop` followed by `booklet`
- Equivalent to manual sequential execution

---

## 4. Error Handling

- Errors shall be reported with a short description.
- Input files shall never be modified in place.

---

## 5. Compatibility

- Paths with spaces shall be supported.
- The CLI shall work on macOS and Windows.
- No network access shall be required.
