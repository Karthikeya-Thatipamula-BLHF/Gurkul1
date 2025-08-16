#!/bin/bash
# ========================================
# RENDER BUILD SCRIPT WITH DISTUTILS FIX
# ========================================
# Fixes Python 3.12 distutils removal issue

set -e  # Exit on any error

echo "🔧 Starting Python 3.12 build with distutils fix..."

# Navigate to Backend directory
cd Backend

# Upgrade pip first
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install setuptools and wheel first to fix distutils
echo "🛠️ Installing build dependencies (setuptools, wheel)..."
pip install "setuptools>=69.0.0" "wheel>=0.42.0"

# Install all requirements
echo "📋 Installing requirements..."
pip install -r requirements_python312_distutils_fix.txt

echo "✅ Build completed successfully!"
