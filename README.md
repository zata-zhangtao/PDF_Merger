# PDF Merger Tool

A cross-platform PDF merger application with both command-line and graphical user interfaces. Merge multiple PDF files into a single document with ease.

## Features

- **Multiple interfaces**: Command-line tool and GUI application
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Flexible merging**: Merge all PDFs in a folder or select specific files
- **Alphabetical ordering**: Files are merged in alphabetical order by default
- **Progress tracking**: Visual feedback during merge operations
- **Error handling**: Robust error handling and logging

## Installation

### Requirements

- Python 3.11 or higher
- PyPDF2 library
- PyQt6 (for GUI mode)

### Using uv (recommended)

```bash
uv sync
```

### Using pip

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

#### Basic usage (merge all PDFs in current directory):
```bash
python merge_pdfs.py
```

#### Specify output filename:
```bash
python merge_pdfs.py output.pdf
```

#### Specify folder and output filename:
```bash
python merge_pdfs.py path/to/folder/ output.pdf
```

#### Show help:
```bash
python merge_pdfs.py --help
```

### Graphical User Interface

Launch the GUI application:
```bash
python merge_pdfs.py --gui
```

Or use the convenience script:
```bash
./start_gui.sh
```

The GUI provides two merge modes:
1. **Folder Mode**: Select a folder containing PDF files to merge all files in alphabetical order
2. **Files Mode**: Manually select specific PDF files to merge in the order chosen

## Building Executables

### Local Build Scripts

Use the provided build scripts to create standalone executables:

```bash
# Build locally
./build_local.sh

# Build using Docker
./build_docker.sh
```

### GitHub Actions

The project includes automated builds for Windows, macOS, and Linux through GitHub Actions. Executables are automatically built on:
- Push to main branch
- Pull requests
- Release creation

## Project Structure

```
concat-pdf/
├── merge_pdfs.py          # Main application with CLI and GUI
├── main.py               # Simple merge script
├── pyproject.toml        # Project configuration
├── requirements.txt      # Python dependencies
├── start_gui.sh         # GUI launcher script
├── build_local.sh       # Local build script
├── build_docker.sh      # Docker build script
├── files/               # Sample PDF files directory
└── .github/workflows/   # CI/CD configuration
```

## API Reference

### Core Functions

#### `merge_pdfs_by_order(pdf_folder, output_filename, exclude_output=True)`
Merge PDF files from a folder in alphabetical order.

**Parameters:**
- `pdf_folder` (str): Path to folder containing PDF files
- `output_filename` (str): Name of the output merged PDF file
- `exclude_output` (bool): Whether to exclude the output file from merging

**Returns:**
- `bool`: True if successful, False otherwise

#### `merge_specific_pdfs(pdf_files, output_filename)`
Merge specific PDF files in the order provided.

**Parameters:**
- `pdf_files` (list): List of PDF file paths to merge
- `output_filename` (str): Name of the output merged PDF file

**Returns:**
- `bool`: True if successful, False otherwise

## Development

### Running Tests

```bash
python test.py
```

### Environment Setup

The project uses uv for dependency management. Create a virtual environment:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. Please check the repository for license details.

## Troubleshooting

### Common Issues

**"No PDF files found"**: Ensure the target directory contains PDF files with `.pdf` extension.

**"Permission denied"**: Check file permissions and ensure the output directory is writable.

**GUI not launching**: Ensure PyQt6 is properly installed:
```bash
pip install PyQt6
```

**Build failures**: Ensure all dependencies are installed and PyInstaller is available:
```bash
pip install pyinstaller
```

## Support

For issues and feature requests, please use the GitHub issue tracker.
