#!/bin/bash
# Setup script for File Ingestion & Retrieval App

echo "=========================================="
echo "File Ingestion & Retrieval App - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create directories
echo ""
echo "Creating data directories..."
mkdir -p data/uploads
mkdir -p data/chroma

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your configuration"
else
    echo ""
    echo ".env file already exists"
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the application: python main.py"
echo "4. Visit http://localhost:8000/docs for API documentation"
echo ""
