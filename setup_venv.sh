#!/bin/bash
# 🔧 Setup Virtual Environment for DSLR System

echo "🔧 Setting up Python Virtual Environment"
echo "========================================"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv dslr_env

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source dslr_env/bin/activate

# Upgrade pip in venv
echo "⬆️ Upgrading pip..."
pip install --upgrade pip setuptools wheel

echo "✅ Virtual environment ready!"
echo ""
echo "📋 To activate manually:"
echo "source ~/standalone-dslr/dslr_env/bin/activate"
echo ""
echo "📋 To install packages:"
echo "pip install -r requirements_minimal.txt"
