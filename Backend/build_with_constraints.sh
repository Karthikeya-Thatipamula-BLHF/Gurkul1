#!/bin/bash
# ========================================
# BUILD SCRIPT WITH DEPENDENCY CONSTRAINTS
# ========================================

set -e

echo "🔧 Building with dependency constraints..."

cd Backend

# Upgrade pip
pip install --upgrade pip

# Install build dependencies
pip install "setuptools>=69.0.0" "wheel>=0.42.0"

# Install with constraints to resolve conflicts
pip install -c constraints.txt -r requirements_production.txt

echo "✅ Build completed with constraints!"
