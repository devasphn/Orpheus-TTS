#!/bin/bash

# Orpheus TTS RunPod - Quick Setup Script
# This script automates the entire setup process
# Run this in RunPod web terminal

set -e

echo "=========================================="
echo "Orpheus TTS RunPod - Quick Setup"
echo "=========================================="
echo ""

# Step 1: Navigate to workspace
echo "Step 1: Navigating to workspace..."
cd /workspace

# Step 2: Clone repository
echo "Step 2: Cloning repository..."
if [ -d "Orpheus-TTS" ]; then
    echo "Repository already exists. Pulling latest changes..."
    cd Orpheus-TTS
    git pull
    cd ..
else
    git clone https://github.com/devasphn/Orpheus-TTS.git
fi

# Step 3: Navigate to deployment directory
echo "Step 3: Navigating to deployment directory..."
cd Orpheus-TTS/runpod_deployment

# Step 4: Create virtual environment (optional)
echo "Step 4: Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Step 5: Activate virtual environment
echo "Step 5: Activating virtual environment..."
source venv/bin/activate

# Step 6: Upgrade pip
echo "Step 6: Upgrading pip..."
pip install --upgrade pip

# Step 7: Install dependencies
echo "Step 7: Installing Python dependencies..."
pip install -r requirements.txt

# Step 8: Install vLLM
echo "Step 8: Installing vLLM 0.7.3..."
pip install vllm==0.7.3

# Step 9: Pre-download model
echo "Step 9: Pre-downloading model (this may take a few minutes)..."
python3 -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('canopylabs/orpheus-tts-0.1-finetune-prod')"

# Step 10: Make startup script executable
echo "Step 10: Making startup script executable..."
chmod +x startup.sh

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start the server, run:"
echo "  python server.py"
echo ""
echo "Then open your browser to:"
echo "  https://your-pod-id-8080.proxy.runpod.net"
echo ""
echo "=========================================="

