import PyPDF2
import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QListWidget, 
                            QFileDialog, QLineEdit, QTextEdit, QMessageBox,
                            QProgressBar, QGroupBox)
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

def main():
    """Main function to handle command line usage"""
    if len(sys.argv) > 1:
        # Command line usage
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("PDF Merger Tool")
            print("Usage:")
            print("  python merge_pdfs.py                    # Merge all PDFs in current directory")
            print("  python merge_pdfs.py output.pdf         # Merge all PDFs with custom output name")
            print("  python merge_pdfs.py folder/ output.pdf # Merge PDFs from specific folder")
            return

        if len(sys.argv) == 2:
            # Custom output filename
            merge_pdfs_by_order(output_filename=sys.argv[1])
        elif len(sys.argv) == 3:
            # Custom folder and output filename
            merge_pdfs_by_order(pdf_folder=sys.argv[1], output_filename=sys.argv[2])
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

class PDFMergerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_files = []
        self.output_folder = ""
        self.output_path = ""
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("PDF Merger Tool")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("PDF Merger Tool")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
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