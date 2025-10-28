#!/bin/bash

# Orpheus TTS RunPod Startup Script
# This script initializes the container and starts the TTS server

set -e

echo "=========================================="
echo "Orpheus TTS RunPod Deployment"
echo "=========================================="
echo ""

# Display system information
echo "System Information:"
echo "-------------------"
echo "Python version: $(python --version)"
echo "CUDA available: $(python -c 'import torch; print(torch.cuda.is_available())')"
echo "CUDA version: $(python -c 'import torch; print(torch.version.cuda if torch.cuda.is_available() else "N/A")')"
echo "GPU count: $(python -c 'import torch; print(torch.cuda.device_count() if torch.cuda.is_available() else 0)')"

if python -c 'import torch; exit(0 if torch.cuda.is_available() else 1)'; then
    echo "GPU name: $(python -c 'import torch; print(torch.cuda.get_device_name(0))')"
    echo "GPU memory: $(python -c 'import torch; print(f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")')"
fi

echo ""
echo "Environment Variables:"
echo "----------------------"
echo "MODEL_NAME: ${MODEL_NAME:-canopylabs/orpheus-tts-0.1-finetune-prod}"
echo "MAX_MODEL_LEN: ${MAX_MODEL_LEN:-2048}"
echo "PORT: ${PORT:-8080}"
echo ""

# Pre-download model if not already cached
echo "Checking model cache..."
python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('${MODEL_NAME:-canopylabs/orpheus-tts-0.1-finetune-prod}')" || echo "Model will be downloaded on first request"

echo ""
echo "Starting Orpheus TTS Server..."
echo "=========================================="
echo ""

# Start the Flask server
exec python server.py

