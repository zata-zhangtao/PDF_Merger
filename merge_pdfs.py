import PyPDF2
import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QLabel, QListWidget,
                            QFileDialog, QLineEdit, QTextEdit, QMessageBox,
                            QProgressBar, QGroupBox, QTabWidget, QComboBox, QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

def merge_pdfs_by_order(pdf_folder="files", output_filename="merged_output.pdf", exclude_output=True):
    """
    Merge PDF files in alphabetical order

    Args:
        pdf_folder (str): Path to folder containing PDF files (default: current directory)
        output_filename (str): Name of the output merged PDF file
        exclude_output (bool): Whether to exclude the output file from merging if it exists

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Convert to Path object for better path handling
        folder_path = Path(pdf_folder)

        if not folder_path.exists():
            print(f"Error: Folder '{pdf_folder}' does not exist.")
            return False

        # Find all PDF files in the folder
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]

        # Exclude the output file if it exists and exclude_output is True
        if exclude_output and output_filename in pdf_files:
            pdf_files.remove(output_filename) 

        if not pdf_files:
            print(f"No PDF files found in '{pdf_folder}'.")
            return False

        # Sort alphabetically (natural sort for numbered files)
        pdf_files.sort()

        print(f"Found {len(pdf_files)} PDF files to merge:")
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"  {i}. {pdf_file}")

        # Create merger object
        merger = PyPDF2.PdfMerger()

        # Add each PDF file to the merger
        for pdf_file in pdf_files:
            file_path = folder_path / pdf_file
            try:
                print(f"Adding: {pdf_file}")
                merger.append(str(file_path))
            except Exception as e:
                print(f"Warning: Could not add {pdf_file}: {e}")
                continue

        # Write the merged PDF
        # Handle both absolute paths and relative filenames
        if os.path.isabs(output_filename):
            output_path = Path(output_filename)
        else:
            output_path = folder_path / output_filename
        with open(output_path, 'wb') as output_file:
            merger.write(output_file)

        merger.close()
        print(f"\nSuccessfully merged {len(pdf_files)} PDFs into '{output_filename}'")
        print(f"Output file location: {output_path.absolute()}")
        return True

    except Exception as e:
        print(f"Error during PDF merging: {e}")
        return False

def merge_specific_pdfs(pdf_files, output_filename="merged_specific.pdf"):
    """
    Merge specific PDF files in the order provided

    Args:
        pdf_files (list): List of PDF file paths to merge
        output_filename (str): Name of the output merged PDF file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Validate that all files exist
        missing_files = []
        for pdf_file in pdf_files:
            if not Path(pdf_file).exists():
                missing_files.append(pdf_file)

        if missing_files:
            print(f"Error: The following files do not exist:")
            for file in missing_files:
                print(f"  - {file}")
            return False

        print(f"Merging {len(pdf_files)} specific PDF files:")
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"  {i}. {pdf_file}")

        merger = PyPDF2.PdfMerger()

        for pdf_file in pdf_files:
            try:
                print(f"Adding: {pdf_file}")
                merger.append(pdf_file)
            except Exception as e:
                print(f"Warning: Could not add {pdf_file}: {e}")
                continue

        # Handle both absolute paths and relative filenames
        output_path = Path(output_filename)
        with open(output_path, 'wb') as output_file:
            merger.write(output_file)

        merger.close()
        print(f"\nSuccessfully merged PDFs into '{output_filename}'")
        return True

    except Exception as e:
        print(f"Error during PDF merging: {e}")
        return False

def compress_pdf(input_file, output_file=None, compression_level='medium'):
    """
    Compress a PDF file to reduce its size

    Args:
        input_file (str): Path to input PDF file
        output_file (str): Path to output compressed PDF file (optional, defaults to input_compressed.pdf)
        compression_level (str): Compression level - 'low', 'medium', or 'high'

    Returns:
        tuple: (bool, dict) - Success status and compression info (original_size, compressed_size, reduction_percent)
    """
    try:
        input_path = Path(input_file)

        if not input_path.exists():
            print(f"Error: File '{input_file}' does not exist.")
            return False, {}

        # Get original file size
        original_size = input_path.stat().st_size

        # Determine output file path
        if output_file is None:
            output_path = input_path.parent / f"{input_path.stem}_compressed.pdf"
        else:
            output_path = Path(output_file)

        print(f"Compressing: {input_file}")
        print(f"Original size: {original_size / 1024:.2f} KB")

        # Read the PDF
        reader = PyPDF2.PdfReader(str(input_path))
        writer = PyPDF2.PdfWriter()

        # Copy all pages to writer
        for page in reader.pages:
            # Compress page content
            page.compress_content_streams()
            writer.add_page(page)

        # Apply compression settings based on level
        if compression_level in ['medium', 'high']:
            # Remove duplicate objects
            writer.add_metadata(reader.metadata)

        # Write compressed PDF
        with open(output_path, 'wb') as output_f:
            if compression_level == 'high':
                writer.write(output_f)
            else:
                writer.write(output_f)

        # Get compressed file size
        compressed_size = output_path.stat().st_size
        reduction_percent = ((original_size - compressed_size) / original_size) * 100

        print(f"Compressed size: {compressed_size / 1024:.2f} KB")
        print(f"Reduction: {reduction_percent:.1f}%")
        print(f"Saved to: {output_path}")

        info = {
            'original_size': original_size,
            'compressed_size': compressed_size,
            'reduction_percent': reduction_percent,
            'output_path': str(output_path)
        }

        return True, info

    except Exception as e:
        print(f"Error during PDF compression: {e}")
        return False, {}

def compress_folder(pdf_folder, output_folder=None, compression_level='medium'):
    """
    Compress all PDF files in a folder

    Args:
        pdf_folder (str): Path to folder containing PDF files
        output_folder (str): Path to output folder (optional, defaults to input_folder/compressed)
        compression_level (str): Compression level - 'low', 'medium', or 'high'

    Returns:
        tuple: (bool, list) - Success status and list of compression results
    """
    try:
        folder_path = Path(pdf_folder)

        if not folder_path.exists():
            print(f"Error: Folder '{pdf_folder}' does not exist.")
            return False, []

        # Determine output folder
        if output_folder is None:
            output_path = folder_path / "compressed"
        else:
            output_path = Path(output_folder)

        # Create output folder if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)

        # Find all PDF files
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]

        if not pdf_files:
            print(f"No PDF files found in '{pdf_folder}'.")
            return False, []

        pdf_files.sort()

        print(f"Found {len(pdf_files)} PDF files to compress")

        results = []
        total_original = 0
        total_compressed = 0

        for pdf_file in pdf_files:
            input_file_path = folder_path / pdf_file
            output_file_path = output_path / pdf_file

            success, info = compress_pdf(str(input_file_path), str(output_file_path), compression_level)

            if success:
                results.append({
                    'filename': pdf_file,
                    'success': True,
                    **info
                })
                total_original += info['original_size']
                total_compressed += info['compressed_size']
            else:
                results.append({
                    'filename': pdf_file,
                    'success': False
                })

            print()  # Empty line between files

        # Print summary
        if total_original > 0:
            total_reduction = ((total_original - total_compressed) / total_original) * 100
            print("=" * 50)
            print("COMPRESSION SUMMARY")
            print("=" * 50)
            print(f"Total original size: {total_original / (1024*1024):.2f} MB")
            print(f"Total compressed size: {total_compressed / (1024*1024):.2f} MB")
            print(f"Total reduction: {total_reduction:.1f}%")
            print(f"Space saved: {(total_original - total_compressed) / (1024*1024):.2f} MB")

        return True, results

    except Exception as e:
        print(f"Error during folder compression: {e}")
        return False, []

def main():
    """Main function to handle command line usage"""
    if len(sys.argv) > 1:
        # Command line usage
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("PDF Merger & Compressor Tool")
            print("\nUsage:")
            print("  Merge PDFs:")
            print("    python merge_pdfs.py                    # Merge all PDFs in current directory")
            print("    python merge_pdfs.py output.pdf         # Merge all PDFs with custom output name")
            print("    python merge_pdfs.py folder/ output.pdf # Merge PDFs from specific folder")
            print("\n  Compress PDFs:")
            print("    python merge_pdfs.py --compress file.pdf                    # Compress single file")
            print("    python merge_pdfs.py --compress file.pdf output.pdf         # Compress with custom output")
            print("    python merge_pdfs.py --compress-folder folder/              # Compress all PDFs in folder")
            print("    python merge_pdfs.py --compress-folder folder/ output_dir/  # Compress with custom output dir")
            print("\n  Compression levels:")
            print("    Add --level=low, --level=medium, or --level=high (default: medium)")
            print("\n  GUI mode:")
            print("    python merge_pdfs.py --gui              # Launch GUI application")
            return

        # Parse compression level
        compression_level = 'medium'
        args = [arg for arg in sys.argv[1:] if not arg.startswith('--level=')]
        for arg in sys.argv[1:]:
            if arg.startswith('--level='):
                level = arg.split('=')[1].lower()
                if level in ['low', 'medium', 'high']:
                    compression_level = level

        # Handle compress commands
        if args[0] == "--compress" and len(args) >= 2:
            input_file = args[1]
            output_file = args[2] if len(args) >= 3 else None
            print(f"Compressing PDF with {compression_level} level...")
            success, info = compress_pdf(input_file, output_file, compression_level)
            if not success:
                sys.exit(1)
            return

        if args[0] == "--compress-folder" and len(args) >= 2:
            input_folder = args[1]
            output_folder = args[2] if len(args) >= 3 else None
            print(f"Compressing folder with {compression_level} level...")
            success, results = compress_folder(input_folder, output_folder, compression_level)
            if not success:
                sys.exit(1)
            return

        # Handle merge commands (original behavior)
        if len(args) == 1:
            # Custom output filename
            merge_pdfs_by_order(output_filename=args[0])
        elif len(args) == 2:
            # Custom folder and output filename
            merge_pdfs_by_order(pdf_folder=args[0], output_filename=args[1])
    else:
        # Default usage - merge all PDFs in current directory
        merge_pdfs_by_order()

class MergeWorker(QThread):
    """Worker thread for PDF merging to prevent GUI freezing"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, pdf_files, output_filename, merge_mode='folder'):
        super().__init__()
        self.pdf_files = pdf_files
        self.output_filename = output_filename
        self.merge_mode = merge_mode

    def run(self):
        try:
            if self.merge_mode == 'folder':
                result = merge_pdfs_by_order(self.pdf_files, self.output_filename)
            else:
                result = merge_specific_pdfs(self.pdf_files, self.output_filename)

            if result:
                self.finished.emit(True, f"Successfully merged PDFs into '{self.output_filename}'")
            else:
                self.finished.emit(False, "Failed to merge PDFs")
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")

class CompressionWorker(QThread):
    """Worker thread for PDF compression to prevent GUI freezing"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str, dict)

    def __init__(self, input_path, output_path, compression_level='medium', compress_mode='file'):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.compression_level = compression_level
        self.compress_mode = compress_mode

    def run(self):
        try:
            if self.compress_mode == 'file':
                success, info = compress_pdf(self.input_path, self.output_path, self.compression_level)
                if success:
                    self.finished.emit(True, "Compression completed successfully!", info)
                else:
                    self.finished.emit(False, "Failed to compress PDF", {})
            else:  # folder mode
                success, results = compress_folder(self.input_path, self.output_path, self.compression_level)
                if success:
                    # Calculate totals
                    total_original = sum(r.get('original_size', 0) for r in results if r.get('success'))
                    total_compressed = sum(r.get('compressed_size', 0) for r in results if r.get('success'))
                    total_reduction = ((total_original - total_compressed) / total_original * 100) if total_original > 0 else 0

                    info = {
                        'original_size': total_original,
                        'compressed_size': total_compressed,
                        'reduction_percent': total_reduction,
                        'files_count': len(results)
                    }
                    self.finished.emit(True, f"Successfully compressed {len(results)} files!", info)
                else:
                    self.finished.emit(False, "Failed to compress folder", {})
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}", {})

class PDFMergerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_files = []
        self.output_folder = ""
        self.output_path = ""
        self.compress_input_path = ""
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("PDF Merger & Compressor Tool")
        self.setGeometry(100, 100, 900, 700)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("PDF Merger & Compressor Tool")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create merge tab
        merge_tab = QWidget()
        self.setup_merge_tab(merge_tab)
        self.tabs.addTab(merge_tab, "Merge PDFs")

        # Create compress tab
        compress_tab = QWidget()
        self.setup_compress_tab(compress_tab)
        self.tabs.addTab(compress_tab, "Compress PDFs")

    def setup_merge_tab(self, tab):
        """Setup the merge PDFs tab"""
        layout = QVBoxLayout(tab)

        # Mode selection
        mode_group = QGroupBox("Merge Mode")
        mode_layout = QVBoxLayout(mode_group)

        # Folder mode
        folder_layout = QHBoxLayout()
        self.folder_btn = QPushButton("Select Folder")
        self.folder_btn.clicked.connect(self.select_folder)
        self.folder_label = QLabel("No folder selected")
        folder_layout.addWidget(self.folder_btn)
        folder_layout.addWidget(self.folder_label)
        mode_layout.addLayout(folder_layout)

        # Files mode
        files_layout = QHBoxLayout()
        self.add_files_btn = QPushButton("Add PDF Files")
        self.add_files_btn.clicked.connect(self.add_files)
        self.clear_files_btn = QPushButton("Clear Files")
        self.clear_files_btn.clicked.connect(self.clear_files)
        files_layout.addWidget(self.add_files_btn)
        files_layout.addWidget(self.clear_files_btn)
        mode_layout.addLayout(files_layout)

        layout.addWidget(mode_group)

        # File list
        list_group = QGroupBox("Selected Files")
        list_layout = QVBoxLayout(list_group)
        self.file_list = QListWidget()
        list_layout.addWidget(self.file_list)
        layout.addWidget(list_group)

        # Output settings
        output_group = QGroupBox("Output Settings")
        output_layout = QVBoxLayout(output_group)

        output_file_layout = QHBoxLayout()
        output_file_layout.addWidget(QLabel("Output file:"))
        self.output_path_field = QLineEdit("merged_output.pdf")
        self.output_path_field.setReadOnly(True)
        self.browse_output_btn = QPushButton("Browse...")
        self.browse_output_btn.clicked.connect(self.select_output_path)
        output_file_layout.addWidget(self.output_path_field)
        output_file_layout.addWidget(self.browse_output_btn)
        output_layout.addLayout(output_file_layout)

        layout.addWidget(output_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Log area
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        layout.addWidget(log_group)

        # Merge button
        self.merge_btn = QPushButton("Merge PDFs")
        self.merge_btn.clicked.connect(self.merge_pdfs)
        self.merge_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(self.merge_btn)

    def setup_compress_tab(self, tab):
        """Setup the compress PDFs tab"""
        layout = QVBoxLayout(tab)

        # Compression mode selection
        mode_group = QGroupBox("Compression Mode")
        mode_layout = QVBoxLayout(mode_group)

        # Radio buttons for mode
        self.compress_mode_group = QButtonGroup()
        self.compress_file_radio = QRadioButton("Compress Single File")
        self.compress_folder_radio = QRadioButton("Compress Folder")
        self.compress_file_radio.setChecked(True)

        self.compress_mode_group.addButton(self.compress_file_radio)
        self.compress_mode_group.addButton(self.compress_folder_radio)

        mode_layout.addWidget(self.compress_file_radio)
        mode_layout.addWidget(self.compress_folder_radio)
        layout.addWidget(mode_group)

        # Input selection
        input_group = QGroupBox("Input Selection")
        input_layout = QVBoxLayout(input_group)

        # File input
        file_input_layout = QHBoxLayout()
        self.compress_input_label = QLabel("No file selected")
        self.compress_select_btn = QPushButton("Select File/Folder")
        self.compress_select_btn.clicked.connect(self.select_compress_input)
        file_input_layout.addWidget(self.compress_input_label)
        file_input_layout.addWidget(self.compress_select_btn)
        input_layout.addLayout(file_input_layout)

        layout.addWidget(input_group)

        # Compression settings
        settings_group = QGroupBox("Compression Settings")
        settings_layout = QVBoxLayout(settings_group)

        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Compression Level:"))
        self.compression_level_combo = QComboBox()
        self.compression_level_combo.addItems(["Low", "Medium", "High"])
        self.compression_level_combo.setCurrentText("Medium")
        level_layout.addWidget(self.compression_level_combo)
        level_layout.addStretch()
        settings_layout.addLayout(level_layout)

        layout.addWidget(settings_group)

        # Output settings
        output_group = QGroupBox("Output Settings")
        output_layout = QVBoxLayout(output_group)

        output_layout.addWidget(QLabel("Output files will be saved with '_compressed' suffix or in 'compressed' folder"))

        output_file_layout = QHBoxLayout()
        output_file_layout.addWidget(QLabel("Custom output:"))
        self.compress_output_field = QLineEdit()
        self.compress_output_field.setPlaceholderText("Optional: custom output path")
        self.compress_browse_btn = QPushButton("Browse...")
        self.compress_browse_btn.clicked.connect(self.select_compress_output)
        output_file_layout.addWidget(self.compress_output_field)
        output_file_layout.addWidget(self.compress_browse_btn)
        output_layout.addLayout(output_file_layout)

        layout.addWidget(output_group)

        # Progress bar
        self.compress_progress_bar = QProgressBar()
        self.compress_progress_bar.setVisible(False)
        layout.addWidget(self.compress_progress_bar)

        # Log area
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        self.compress_log_text = QTextEdit()
        self.compress_log_text.setMaximumHeight(150)
        log_layout.addWidget(self.compress_log_text)
        layout.addWidget(log_group)

        # Compress button
        self.compress_btn = QPushButton("Compress PDFs")
        self.compress_btn.clicked.connect(self.compress_pdfs)
        self.compress_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(self.compress_btn)
        
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select PDF Folder")
        if folder:
            self.output_folder = folder
            self.folder_label.setText(f"Folder: {folder}")
            self.load_folder_files(folder)
            
    def load_folder_files(self, folder):
        self.file_list.clear()
        pdf_files = [f for f in os.listdir(folder) if f.lower().endswith('.pdf')]
        pdf_files.sort()
        
        for pdf_file in pdf_files:
            self.file_list.addItem(pdf_file)
        
        self.log(f"Found {len(pdf_files)} PDF files in folder")
        
    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF Files", "", "PDF Files (*.pdf)"
        )
        if files:
            for file in files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
                    self.file_list.addItem(os.path.basename(file))
            
            self.log(f"Added {len(files)} files")
            
    def clear_files(self):
        self.selected_files.clear()
        self.file_list.clear()
        self.log("Cleared all selected files")
        
    def select_output_path(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Merged PDF As", 
            "merged_output.pdf",
            "PDF Files (*.pdf);;All Files (*)"
        )
        if file_path:
            # Ensure .pdf extension
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'
            self.output_path = file_path
            self.output_path_field.setText(file_path)
            self.log(f"Output path set to: {file_path}")
        
    def log(self, message):
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
        
    def merge_pdfs(self):
        # Determine output path
        output_path = self.output_path if self.output_path else self.output_path_field.text().strip()
        
        if not output_path:
            QMessageBox.warning(self, "Warning", "Please select an output file path")
            return
            
        # Ensure .pdf extension
        if not output_path.lower().endswith('.pdf'):
            output_path += '.pdf'
            
        if self.output_folder:
            # Folder mode
            self.start_merge_worker(self.output_folder, output_path, 'folder')
        elif self.selected_files:
            # Files mode
            self.start_merge_worker(self.selected_files, output_path, 'files')
        else:
            QMessageBox.warning(self, "Warning", "Please select a folder or add PDF files")
            return
            
    def start_merge_worker(self, files, output_filename, mode):
        self.merge_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        self.worker = MergeWorker(files, output_filename, mode)
        self.worker.progress.connect(self.log)
        self.worker.finished.connect(self.on_merge_finished)
        self.worker.start()
        
    def on_merge_finished(self, success, message):
        self.progress_bar.setVisible(False)
        self.merge_btn.setEnabled(True)

        if success:
            QMessageBox.information(self, "Success", message)
            self.log("Merge completed successfully!")
        else:
            QMessageBox.critical(self, "Error", message)
            self.log(f"Merge failed: {message}")

    # Compression tab methods
    def select_compress_input(self):
        """Select input file or folder for compression"""
        if self.compress_file_radio.isChecked():
            # Select single file
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select PDF File to Compress", "", "PDF Files (*.pdf)"
            )
            if file_path:
                self.compress_input_path = file_path
                self.compress_input_label.setText(f"File: {os.path.basename(file_path)}")
                self.compress_log(f"Selected file: {file_path}")
        else:
            # Select folder
            folder = QFileDialog.getExistingDirectory(self, "Select Folder to Compress")
            if folder:
                self.compress_input_path = folder
                pdf_count = len([f for f in os.listdir(folder) if f.lower().endswith('.pdf')])
                self.compress_input_label.setText(f"Folder: {folder} ({pdf_count} PDFs)")
                self.compress_log(f"Selected folder: {folder} with {pdf_count} PDF files")

    def select_compress_output(self):
        """Select output path for compressed PDFs"""
        if self.compress_file_radio.isChecked():
            # Select output file
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Compressed PDF As",
                "",
                "PDF Files (*.pdf);;All Files (*)"
            )
            if file_path:
                if not file_path.lower().endswith('.pdf'):
                    file_path += '.pdf'
                self.compress_output_field.setText(file_path)
                self.compress_log(f"Output path set to: {file_path}")
        else:
            # Select output folder
            folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
            if folder:
                self.compress_output_field.setText(folder)
                self.compress_log(f"Output folder set to: {folder}")

    def compress_log(self, message):
        """Add message to compression log"""
        self.compress_log_text.append(message)
        self.compress_log_text.verticalScrollBar().setValue(
            self.compress_log_text.verticalScrollBar().maximum()
        )

    def compress_pdfs(self):
        """Start PDF compression"""
        if not hasattr(self, 'compress_input_path') or not self.compress_input_path:
            QMessageBox.warning(self, "Warning", "Please select a file or folder to compress")
            return

        # Get compression level
        compression_level = self.compression_level_combo.currentText().lower()

        # Get output path
        output_path = self.compress_output_field.text().strip() if self.compress_output_field.text().strip() else None

        # Determine mode
        if self.compress_file_radio.isChecked():
            mode = 'file'
        else:
            mode = 'folder'

        self.start_compress_worker(self.compress_input_path, output_path, compression_level, mode)

    def start_compress_worker(self, input_path, output_path, compression_level, mode):
        """Start compression worker thread"""
        self.compress_btn.setEnabled(False)
        self.compress_progress_bar.setVisible(True)
        self.compress_progress_bar.setRange(0, 0)  # Indeterminate progress

        self.compress_worker = CompressionWorker(input_path, output_path, compression_level, mode)
        self.compress_worker.progress.connect(self.compress_log)
        self.compress_worker.finished.connect(self.on_compress_finished)
        self.compress_worker.start()

    def on_compress_finished(self, success, message, info):
        """Handle compression completion"""
        self.compress_progress_bar.setVisible(False)
        self.compress_btn.setEnabled(True)

        if success:
            # Build detailed message
            details = f"{message}\n\n"
            if 'files_count' in info:
                details += f"Files processed: {info['files_count']}\n"
            details += f"Original size: {info['original_size'] / (1024*1024):.2f} MB\n"
            details += f"Compressed size: {info['compressed_size'] / (1024*1024):.2f} MB\n"
            details += f"Reduction: {info['reduction_percent']:.1f}%\n"
            details += f"Space saved: {(info['original_size'] - info['compressed_size']) / (1024*1024):.2f} MB"

            QMessageBox.information(self, "Success", details)
            self.compress_log("Compression completed successfully!")
            self.compress_log(details)
        else:
            QMessageBox.critical(self, "Error", message)
            self.compress_log(f"Compression failed: {message}")

def run_gui():
    """Run the GUI application"""
    app = QApplication(sys.argv)
    window = PDFMergerGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        run_gui()
    else:
        main()