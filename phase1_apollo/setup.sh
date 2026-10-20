#!/bin/bash

echo "🚀 Setting up Phase 1 Apollo Scraper..."

# Create virtual environment (optional)
# python3 -m venv venv
# source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create .env from example
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your Apollo API key!"
else
    echo "✓ .env file already exists"
fi

# Create output directory if it doesn't exist
mkdir -p output

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your Apollo API key"
echo "2. Customize config.py if needed (scoring keywords, etc.)"
echo "3. Edit main.py with your target company domains"
echo "4. Run: python main.py"
