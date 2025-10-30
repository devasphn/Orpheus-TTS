#!/bin/bash

# Real-time GPU Monitoring Script for Orpheus TTS
# This script monitors GPU utilization during TTS generation

echo "=========================================="
echo "  Orpheus TTS GPU Real-time Monitor"
echo "  RTX A4500 Performance Tracking"
echo "=========================================="
echo ""
echo "This script will monitor GPU utilization in real-time."
echo "Run this in a SEPARATE terminal while making TTS requests."
echo ""
echo "Press Ctrl+C to stop monitoring"
echo ""
echo "Starting in 3 seconds..."
sleep 3

# Check if nvidia-smi is available
if ! command -v nvidia-smi &> /dev/null; then
    echo "ERROR: nvidia-smi not found!"
    echo "Make sure NVIDIA drivers are installed."
    exit 1
fi

echo ""
echo "=========================================="
echo "GPU Utilization Monitor (1 second intervals)"
echo "=========================================="
echo ""
echo "Legend:"
echo "  gpu   = GPU utilization percentage"
echo "  mem   = Memory utilization percentage"
echo "  enc   = Encoder utilization"
echo "  dec   = Decoder utilization"
echo ""
echo "Expected during TTS generation:"
echo "  GPU: 15-45% (spikes during inference)"
echo "  MEM: 80-90% (model loaded in memory)"
echo ""
echo "If you see 0% GPU consistently, it means:"
echo "  1. No inference is running (idle)"
echo "  2. GPU bursts are very short (sampling artifact)"
echo ""
echo "Starting monitoring..."
echo ""

# Run nvidia-smi in device monitoring mode
# -s u = show utilization stats
# -d 1 = update every 1 second
nvidia-smi dmon -s u -d 1

