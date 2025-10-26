#!/bin/bash

# Docker-based cross-platform build script
# Builds executables for Windows, macOS, and Linux using Docker

echo "🐳 Starting Docker-based cross-platform build..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Create build directory
mkdir -p dist

echo "🪟 Building Windows executable..."
docker run --rm -v $(pwd):/app -w /app python:3.11-windowsservercore powershell -Command "
    pip install -r requirements.txt pyinstaller;
    pyinstaller --noconsole --onefile --name PDF-Merger-Windows merge_pdfs.py;
    Copy-Item dist/PDF-Merger-Windows.exe /app/dist/
"

echo "🐧 Building Linux executable..."
docker run --rm -v $(pwd):/app -w /app python:3.11-slim bash -c "
    apt-get update && apt-get install -y libxcb-xinerama0;
    pip install -r requirements.txt pyinstaller;
    pyinstaller --onefile --name PDF-Merger-Linux merge_pdfs.py;
    cp dist/PDF-Merger-Linux /app/dist/
"

echo "✅ Cross-platform build completed!"
echo "📁 Built files:"
ls -la dist/

echo ""
echo "Usage:"
echo "  Windows: dist/PDF-Merger-Windows.exe --gui"
echo "  Linux:   dist/PDF-Merger-Linux --gui"