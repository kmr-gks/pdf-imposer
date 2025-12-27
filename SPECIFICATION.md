
# CLI Specification — pdf-imposer

This document defines the command-line interface (CLI) behavior for `pdf-imposer`.

---

## 1. Command Name

Primary command:

- `pdf-imposer`

(If installed as a Python package, it should also be invokable as `python -m pdf_imposer`.)

---

## 2. Global Behavior

### 2.1 Help

- `pdf-imposer --help` shall show top-level help with available subcommands.
- `pdf-imposer <subcommand> --help` shall show subcommand-specific help.

### 2.2 Verbosity

- `-v, --verbose` enables verbose logs (debug-oriented messages).
- Without `--verbose`, output shall be minimal and user-friendly.

### 2.3 Exit Codes

- `0`: Success
- `1`: General error (unexpected exception)
- `2`: CLI usage error (invalid arguments, missing files, etc.)
- `3`: Input PDF error (cannot open/read/parse)
- `4`: Output write error (cannot write output file)

### 2.4 Common Error Message Rules

Errors shall be printed to stderr and include:
- a short description of the failure
- the path involved (when applicable)
- a hint to use `--verbose` when additional debug details exist

Example:
- `Error: failed to open input PDF: input.pdf (file not found)`

---

## 3. Common Options and Arguments

All subcommands share:

### 3.1 Input

- `INPUT` (positional): path to an input PDF file

Rules:
- If `INPUT` does not exist, exit with code `2`.
- If `INPUT` exists but is not a readable PDF, exit with code `3`.

### 3.2 Output

- `-o, --output OUTPUT` (required): path to the output PDF file

Rules:
- If `OUTPUT` parent directory does not exist, exit with code `2`.
- If `OUTPUT` exists, behavior depends on `--overwrite`.
- Default: do not overwrite.

### 3.3 Overwrite

- `--overwrite`: allow overwriting an existing output file

Rules:
- If `OUTPUT` exists and `--overwrite` is not given, exit with code `2` and an
  explanatory message.

---

## 4. Subcommands

### 4.1 `crop`

Remove excessive whitespace/margins by detecting page content bounds.

**Usage**
```bash
pdf-imposer crop INPUT -o OUTPUT [options]
````

**Options**

* `--margin PT` (default: `0`)

  * Additional margin around detected content in points (1/72 inch).
  * Must be `>= 0`.
* `--min-area RATIO` (default: `0.0005`)

  * Ignore detected content boxes smaller than this fraction of the page area
    (helps avoid cropping based on tiny artifacts).
  * Must be `> 0` and `< 1`.
* `--keep-empty-pages` (default: enabled)

  * If a page has no detectable content, keep it unchanged.
  * (If disabled in future, such pages could be removed; out of scope now.)
* `--verbose` (global)

**Behavior**

* For each page:

  * detect visible content bounding boxes
  * compute a union bounding rectangle
  * expand by `--margin`
  * clamp within page bounds
  * set the page crop box accordingly
* If no content is detected on a page, the page shall remain unchanged.
* The output shall be saved as a new PDF.

**Examples**

```bash
pdf-imposer crop input.pdf -o cropped.pdf
pdf-imposer crop input.pdf -o cropped.pdf --margin 6
```

---

### 4.2 `booklet`

Generate a booklet-imposed PDF (page order and printing layout preparation).

**Usage**

```bash
pdf-imposer booklet INPUT -o OUTPUT [options]
```

**Options**

* `--pad` / `--no-pad` (default: `--pad`)

  * If enabled, pad total pages to a multiple of 4 by adding blank pages.
  * If disabled and page count is not a multiple of 4, exit with code `2`.
* `--paper` (default: `auto`)

  * Accepted: `auto`, `A4`, `Letter`
  * `auto` keeps the original page size for now (future: fit to selected paper).
* `--mode` (default: `order-only`)

  * Accepted: `order-only`, `2up`
  * `order-only`: output is a reordered single-page sequence (safe baseline).
  * `2up`: output is imposed into two pages per sheet (may be implemented later).
* `--verbose` (global)

**Booklet Page Ordering Rule**

* Let `N` be the total number of pages after padding (must be multiple of 4).
* For each sheet, output two “spreads”:

  * spread 1: `(N-1, 0)`, then `(1, N-2)`, repeating inward
  * spread 2: `(2, N-3)`, then `(N-4, 3)`, repeating inward
* The implementation must be unit-tested via pure functions returning page indices.

*(Note: Exact internal representation may differ; acceptance is based on correct ordering.)*

**Examples**

```bash
pdf-imposer booklet input.pdf -o booklet.pdf
pdf-imposer booklet input.pdf -o booklet.pdf --no-pad
pdf-imposer booklet input.pdf -o booklet.pdf --mode order-only
```

---

### 4.3 `auto`

Run a default pipeline intended for typical printing.

**Usage**

```bash
pdf-imposer auto INPUT -o OUTPUT [options]
```

**Options**

* `--margin PT` (default: `0`)

  * Passed to `crop`.
* `--pad` / `--no-pad` (default: `--pad`)

  * Passed to `booklet`.
* `--mode` (default: `order-only`)

  * Passed to `booklet`.
* `--verbose` (global)

**Behavior**

* The tool shall:

  1. crop margins
  2. apply booklet transformation
* Intermediate files shall not be written to disk unless `--verbose` and a future
  debug option is added.

**Examples**

```bash
pdf-imposer auto input.pdf -o print-ready.pdf
pdf-imposer auto input.pdf -o print-ready.pdf --margin 6 --mode order-only
```

---

## 5. Logging Output (Guidelines)

Without `--verbose`, show:

* one-line start message (optional)
* one-line completion summary (pages processed, output path)

With `--verbose`, show:

* detected page count
* per-page crop results (old box -> new box) where feasible
* booklet padding details and final page count
* stack traces on unexpected exceptions

---

## 6. Compatibility Notes

* Paths must support spaces.
* Input/output encoding should be UTF-8 safe on macOS and Windows.
* The tool shall not require network access.
