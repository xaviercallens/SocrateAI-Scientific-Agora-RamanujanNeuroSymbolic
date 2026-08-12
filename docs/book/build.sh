#!/bin/bash
# Task 5.7: Pandoc Generation Pipeline
# Builds the English and French PDFs using Pandoc and the LaTeX template.

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "==========================================="
echo " RAMA Book Generation Pipeline (Pandoc)"
echo "==========================================="

# Check if Pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo "[!] Pandoc is not installed. Please install pandoc to generate the PDFs."
    echo "    e.g., sudo apt install pandoc texlive-latex-base texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra"
    exit 1
fi

TEMPLATE="templates/rama_book.tex"

# Build English Book
if [ -f "en/main.md" ]; then
    echo "[*] Building English PDF..."
    pandoc en/metadata.yaml en/main.md \
        --template="$TEMPLATE" \
        -o en/rama_compendium_en.pdf \
        --pdf-engine=pdflatex
    echo "    -> Output: en/rama_compendium_en.pdf"
else
    echo "[!] en/main.md not found. Generate the markdown first."
fi

# Build French Book
if [ -f "fr/main.md" ]; then
    echo "[*] Building French PDF..."
    pandoc fr/metadata.yaml fr/main.md \
        --template="$TEMPLATE" \
        -o fr/rama_compendium_fr.pdf \
        --pdf-engine=pdflatex
    echo "    -> Output: fr/rama_compendium_fr.pdf"
else
    echo "[!] fr/main.md not found. Generate the markdown first."
fi

echo "[*] Pipeline finished."
