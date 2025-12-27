# Requirements Specification — pdf-imposer

## 1. Overview

`pdf-imposer` is a Python command-line tool that optimizes PDF files for printing on macOS and Windows.
It provides utilities to crop PDFs, create booklet-formatted PDFs, and run automated processing pipelines.

The project is CLI-first and designed for local, offline use.

---

## 2. Target Users

- Users who frequently print PDF documents (students, researchers, office workers)
- Users who want to reduce margins and save paper
- Users who want to create booklet-style printed documents

---

## 3. Supported Platforms

- macOS
- Windows

(Linux is not a primary target but may work.)

---

## 4. Functional Requirements

### 4.1 Crop

- The tool shall provide a `crop` command.
- The command shall auto-detect content bounding boxes for each page using PyMuPDF.
- Margins around detected content shall be reduced.
- A configurable margin value shall be supported.
- The output shall be a new PDF file.

---

### 4.2 Booklet

- The tool shall provide a `booklet` command.
- The command shall reorder pages for booklet-style printing.
- The total page count shall be padded to a multiple of 4 by adding blank pages if necessary.
- Page order shall follow standard booklet printing rules.

---

### 4.3 Auto Pipeline

- The tool shall provide an `auto` command.
- The command shall run the crop step followed by the booklet step.
- The behavior shall be equivalent to manually running `crop` and then `booklet`.

---

## 5. Non-Functional Requirements

### 5.1 Performance

- The tool shall process typical PDFs (tens to hundreds of pages) within reasonable time on consumer hardware.

### 5.2 Usability

- Commands and options shall be simple and discoverable via `--help`.
- Error messages shall be concise and user-friendly.

### 5.3 Maintainability

- The codebase shall be modular.
- Core logic (e.g., booklet page ordering) shall be testable with unit tests.

---

## 6. Constraints

- Implementation language: Python
- Offline operation only (no network dependency)
- Open-source libraries shall be used for PDF processing

---

## 7. Out of Scope

- GUI application
- PDF preview or interactive editing
- Advanced layout customization beyond margin control and booklet reordering

---

## 8. Acceptance Criteria

- The `crop` command reduces visible margins in output PDFs.
- The `booklet` command produces correct page order for folded booklets.
- The `auto` command successfully combines crop and booklet processing.
- All commands run on macOS and Windows.


