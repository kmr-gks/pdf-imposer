# pdf-imposer

A Python tool to optimize PDFs for printing on macOS and Windows. This tool provides utilities to crop PDFs, create booklet-formatted PDFs, and run automated processing pipelines.

## Features

- **Crop**: Auto-detect content bounding boxes and remove margins using PyMuPDF
- **Booklet**: Pad pages to a multiple of 4 and reorder for booklet printing using pypdf
- **Auto**: Run a complete pipeline (crop + booklet) with a single command

## Installation

### From source

```bash
git clone https://github.com/kmr-gks/pdf-imposer.git
cd pdf-imposer
pip install -e .
```

### For development

```bash
pip install -e ".[dev]"
```

## Usage

### Crop command

Remove margins from a PDF by auto-detecting content boundaries:

```bash
pdf-imposer crop input.pdf output-cropped.pdf
```

With custom margin:

```bash
pdf-imposer crop input.pdf output-cropped.pdf --margin 20
```

### Booklet command

Reorder pages for booklet-style printing (double-sided, fold in half):

```bash
pdf-imposer booklet input.pdf output-booklet.pdf
```

This command:
- Pads the page count to the nearest multiple of 4 (adds blank pages if needed)
- Reorders pages so that when printed double-sided and folded, they appear in correct sequence

### Auto command

Run the complete pipeline (crop then booklet):

```bash
pdf-imposer auto input.pdf output-final.pdf
```

With custom margin:

```bash
pdf-imposer auto input.pdf output-final.pdf --margin 15
```

### Help

Get help for any command:

```bash
pdf-imposer --help
pdf-imposer crop --help
pdf-imposer booklet --help
pdf-imposer auto --help
```

## How Booklet Printing Works

Booklet printing arranges pages so that when you:
1. Print double-sided
2. Fold the pages in half
3. Staple along the fold

The pages appear in the correct reading order. For example, a 4-page document becomes:
- Front of sheet: Pages 4 and 1 (side by side)
- Back of sheet: Pages 2 and 3 (side by side)

When folded, you read: 1, 2, 3, 4.

## Development

### Running tests

```bash
pytest
```

### Linting

```bash
ruff check .
ruff format .
```

### Running from source

```bash
python -m pdf_imposer.cli --help
```

## Requirements

- Python >= 3.8
- PyMuPDF >= 1.23.0
- pypdf >= 3.0.0
- click >= 8.0.0

## License

MIT License - see LICENSE file for details.