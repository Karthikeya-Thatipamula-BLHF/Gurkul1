#!/bin/bash
# ========================================
# BUILD WITH LANGCHAIN CONSTRAINTS
# ========================================

set -e

echo "🔧 Building with LangChain constraints..."

cd Backend

# Upgrade pip
pip install --upgrade pip

# Install build dependencies
pip install "setuptools>=69.0.0" "wheel>=0.42.0"

# Install with constraints to resolve LangChain conflicts
pip install -c constraints_langchain.txt -r requirements_production.txt

echo "✅ Build completed with LangChain constraints!"
