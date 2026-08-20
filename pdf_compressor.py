#!/usr/bin/env python3
# Author: Theeko74
# Contributor(s): skjerns
# Oct, 2021
# MIT license -- free to use as you want, cheers.

"""
Simple python wrapper script to use ghoscript function to compress PDF files.

Compression levels:
    0: default
    1: prepress
    2: printer
    3: ebook
    4: screen

By default the CLI takes every PDF inside the `input` folder and writes the
compressed copies to `output`, mirroring the sub-folder structure. A single file
can still be passed explicitly as an argument.

Dependency: Ghostscript.
On MacOSX install via command line `brew install ghostscript`.
"""

import argparse
import subprocess
import os.path
import sys
import shutil

INPUT_DIR = 'input'
OUTPUT_DIR = 'output'


def compress(input_file_path, output_file_path, power=0):
    """Function to compress PDF via Ghostscript command line interface"""
    quality = {
        0: '/default',
        1: '/prepress',
        2: '/printer',
        3: '/ebook',
        4: '/screen'
    }

    # Basic controls
    # Check if valid path
    if not os.path.isfile(input_file_path):
        print("Error: invalid path for input PDF file")
        sys.exit(1)

    # Check if file is a PDF by extension
    if input_file_path.split('.')[-1].lower() != 'pdf':
        print("Error: input file is not a PDF")
        sys.exit(1)

    gs = get_ghostscript_path()
    print("Compress PDF...")
    initial_size = os.path.getsize(input_file_path)
    subprocess.call([gs, '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                    '-dPDFSETTINGS={}'.format(quality[power]),
                    '-dNOPAUSE', '-dQUIET', '-dBATCH',
                    '-sOutputFile={}'.format(output_file_path),
                     input_file_path]
    )
    final_size = os.path.getsize(output_file_path)
    ratio = 1 - (final_size / initial_size)
    print("Compression by {0:.0%}.".format(ratio))
    print("Final file size is {0:.1f}MB".format(final_size / 1000000))
    print("Done.")


def get_ghostscript_path():
    gs_names = ['gs', 'gswin32', 'gswin64']
    for name in gs_names:
        if shutil.which(name):
            return shutil.which(name)
    raise FileNotFoundError(f'No GhostScript executable was found on path ({"/".join(gs_names)})')


def iter_pdfs(root):
    """Yield every PDF under `root`, recursively, in a stable order."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in sorted(filenames):
            if name.lower().endswith('.pdf'):
                yield os.path.join(dirpath, name)


def compress_dir(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR, power=2):
    """Compress every PDF from `input_dir` into `output_dir`.

    The sub-folder structure is mirrored: a PDF sitting loose in `input`
    lands loose in `output`, and a PDF inside `input/lote` lands in
    `output/lote`. Returns the list of files written.
    """
    if not os.path.isdir(input_dir):
        print("Error: input folder '{}' not found".format(input_dir))
        sys.exit(1)

    pdf_files = list(iter_pdfs(input_dir))
    if not pdf_files:
        print("No PDF found in '{}'. Nothing to do.".format(input_dir))
        return []

    print("Found {} PDF file(s) in '{}'.".format(len(pdf_files), input_dir))
    print()

    written = []
    initial_total = 0
    final_total = 0
    for input_file_path in pdf_files:
        relative_path = os.path.relpath(input_file_path, input_dir)
        output_file_path = os.path.join(output_dir, relative_path)
        os.makedirs(os.path.dirname(output_file_path) or '.', exist_ok=True)

        print("-> {}".format(relative_path))
        initial_total += os.path.getsize(input_file_path)
        compress(input_file_path, output_file_path, power=power)
        final_total += os.path.getsize(output_file_path)
        written.append(output_file_path)
        print()

    ratio = 1 - (final_total / initial_total)
    print("{} file(s) written to '{}'.".format(len(written), output_dir))
    print("Total: {0:.1f}MB -> {1:.1f}MB ({2:.0%}).".format(
        initial_total / 1000000, final_total / 1000000, ratio))
    return written


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('input', nargs='?',
                        help="Relative or absolute path of the input PDF file. "
                             "When omitted, every PDF in the '{}' folder is "
                             "compressed into '{}'.".format(INPUT_DIR, OUTPUT_DIR))
    parser.add_argument('-o', '--out', help='Relative or absolute path of the output PDF file '
                                            '(or of the output folder, in folder mode)')
    parser.add_argument('-c', '--compress', type=int, help='Compression level from 0 to 4')
    parser.add_argument('-b', '--backup', action='store_true', help="Backup the old PDF file")
    parser.add_argument('--open', action='store_true', default=False,
                        help='Open PDF after compression')
    args = parser.parse_args()

    # In case no compression level is specified, default is 2 '/ printer'
    if not args.compress:
        args.compress = 2

    # Folder mode: 'input' -> 'output', never touching the source files
    if args.input is None:
        compress_dir(INPUT_DIR, args.out or OUTPUT_DIR, power=args.compress)
        return

    # In case no output file is specified, store in temp file
    if not args.out:
        args.out = 'temp.pdf'

    # Run
    compress(args.input, args.out, power=args.compress)

    # In case no output file is specified, erase original file
    if args.out == 'temp.pdf':
        if args.backup:
            shutil.copyfile(args.input, args.input.replace(".pdf", "_BACKUP.pdf"))
        shutil.copyfile(args.out, args.input)
        os.remove(args.out)

    # In case we want to open the file after compression
    if args.open:
        if args.out == 'temp.pdf' and args.backup:
            subprocess.call(['open', args.input])
        else:
            subprocess.call(['open', args.out])

if __name__ == '__main__':
    main()
