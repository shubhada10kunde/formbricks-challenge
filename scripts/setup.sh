#!/bin/bash

echo "🚀 Setting up Formbricks Challenge..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p data

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your API keys"
fi

# Make scripts executable
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x main.py

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Start Formbricks: python main.py formbricks up"
echo "4. Generate data: python main.py formbricks generate"
echo "5. Seed data: python main.py formbricks seed"