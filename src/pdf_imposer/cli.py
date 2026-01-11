"""Command-line interface for PDF Imposer."""

import sys
from pathlib import Path

import click

from . import __version__
from .booklet_pdf import create_booklet_pdf
from .crop import crop_pdf


@click.group()
@click.version_option(version=__version__)
def main():
    """PDF Imposer - Optimize PDFs for printing on macOS and Windows."""
    pass


def _default_output_path(input_pdf: str, suffix: str) -> str:
    p = Path(input_pdf)
    # input.pdf -> input-<suffix>.pdf
    return str(p.with_name(f"{p.stem}-{suffix}{p.suffix or '.pdf'}"))


@main.command()
@click.argument("input_pdf", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_pdf", required=False, type=click.Path(dir_okay=False))
@click.option(
    "--margin",
    default=10,
    type=float,
    help="Margin to preserve around content in points (default: 10)",
)
@click.option("--overwrite", is_flag=True, help="Overwrite output file if it exists.")
def crop(input_pdf, output_pdf, margin, overwrite):
    """
    Auto-detect content bounding box and remove margins.

    This command analyzes each page to find the content boundaries and crops
    the PDF to remove unnecessary white space, while preserving a small margin.
    """
    if output_pdf is None:
        output_pdf = _default_output_path(input_pdf, "cropped")

    out_path = Path(output_pdf)
    if out_path.exists() and not overwrite:
        raise click.ClickException(
            f"Output file already exists: {output_pdf} (use --overwrite to replace)"
        )
    try:
        click.echo(f"Cropping {input_pdf}...")
        crop_pdf(input_pdf, output_pdf, margin=margin)
        click.echo(f"Cropped PDF saved to {output_pdf}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("input_pdf", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_pdf", required=False, type=click.Path(dir_okay=False))
@click.option("--overwrite", is_flag=True, help="Overwrite output file if it exists.")
def booklet(input_pdf, output_pdf, overwrite):
    """
    Reorder pages for booklet printing.

    This command pads the page count to a multiple of 4 and reorders pages
    so that when printed double-sided and folded in half, the pages appear
    in the correct sequence.
    """
    if output_pdf is None:
        output_pdf = _default_output_path(input_pdf, "booklet")
    out_path = Path(output_pdf)
    if out_path.exists() and not overwrite:
        raise click.ClickException(
            f"Output file already exists: {output_pdf} (use --overwrite to replace)"
        )
    try:
        click.echo(f"Creating booklet from {input_pdf}...")
        create_booklet_pdf(input_pdf, output_pdf)
        click.echo(f"Booklet PDF saved to {output_pdf}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("input_pdf", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_pdf", required=False, type=click.Path(dir_okay=False))
@click.option(
    "--margin",
    default=10,
    type=float,
    help="Margin to preserve around content in points (default: 10)",
)
@click.option("--overwrite", is_flag=True, help="Overwrite output file if it exists.")
def auto(input_pdf, output_pdf, margin, overwrite):
    """
    Run a basic pipeline: crop then booklet.

    This command applies both cropping and booklet formatting in sequence,
    creating an optimized PDF ready for booklet-style printing.
    """
    if output_pdf is None:
        output_pdf = _default_output_path(input_pdf, "final")

    out_path = Path(output_pdf)
    if out_path.exists() and not overwrite:
        raise click.ClickException(
            f"Output file already exists: {output_pdf} (use --overwrite to replace)"
        )

    # 中間ファイル：outputと衝突しない名前にする
    temp_path = out_path.with_suffix(".tmp.pdf")

    try:
        click.echo(f"Processing {input_pdf} -> {output_pdf} ...")
        click.echo("Step 1: Cropping...")
        crop_pdf(input_pdf, str(temp_path), margin=margin)

        click.echo("Step 2: Creating booklet...")
        create_booklet_pdf(str(temp_path), output_pdf)

        # Clean up temporary file
        if temp_path.exists():
            temp_path.unlink()

        click.echo(f"Processed PDF saved to {output_pdf}")
    except Exception as e:
        # Clean up temporary file if it exists
        if temp_path.exists():
            temp_path.unlink()
        raise click.ClickException(str(e))


if __name__ == "__main__":
    main()
