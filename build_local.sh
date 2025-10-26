#!/bin/bash

# Local Build Script for PDF Merger
# This script builds the application for the current platform

echo "🚀 Starting PDF Merger build process..."

# Check if we're in the correct directory
if [ ! -f "merge_pdfs.py" ]; then
    echo "❌ Error: merge_pdfs.py not found. Please run this script from the project root."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Detect platform and build accordingly
platform=$(uname -s)
case $platform in
    "Darwin")
        echo "🍎 Building for macOS..."
        pyinstaller --noconsole --onefile --windowed --name "PDF-Merger" merge_pdfs.py
        echo "✅ macOS build completed: dist/PDF-Merger"
        ;;
    "Linux")
        echo "🐧 Building for Linux..."
        pyinstaller --onefile --name "PDF-Merger" merge_pdfs.py
        echo "✅ Linux build completed: dist/PDF-Merger"
        ;;
    "MINGW"*|"CYGWIN"*|"MSYS"*)
        echo "🪟 Building for Windows..."
        pyinstaller --noconsole --onefile --name "PDF-Merger" merge_pdfs.py
        echo "✅ Windows build completed: dist/PDF-Merger.exe"
        ;;
    *)
        echo "❓ Unknown platform: $platform"
        echo "🔄 Attempting generic build..."
        pyinstaller --onefile --name "PDF-Merger" merge_pdfs.py
        ;;
esac

# Test the build
echo "🧪 Testing the built executable..."
if [ -f "dist/PDF-Merger" ] || [ -f "dist/PDF-Merger.exe" ]; then
    echo "✅ Build successful!"
    echo "📁 Executable location: $(pwd)/dist/"
    ls -la dist/
else
    echo "❌ Build failed! Check the output above for errors."
    exit 1
fi

echo "🎉 Build process completed!"
echo ""
echo "To run the GUI:"
case $platform in
    "Darwin"|"Linux")
        echo "  ./dist/PDF-Merger --gui"
        ;;
    "MINGW"*|"CYGWIN"*|"MSYS"*)
        echo "  dist/PDF-Merger.exe --gui"
        ;;
esac