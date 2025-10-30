#!/usr/bin/env python3
"""
GPU Diagnostic Script for Orpheus TTS on RTX A4500
This script verifies GPU configuration and identifies performance bottlenecks.
"""

import os
import sys
import time
import subprocess
import torch

def print_header(text):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def check_cuda_availability():
    """Check if CUDA is available and working"""
    print_header("1. CUDA Availability Check")
    
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"Number of GPUs: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            print(f"\nGPU {i}:")
            print(f"  Name: {torch.cuda.get_device_name(i)}")
            print(f"  Memory: {torch.cuda.get_device_properties(i).total_memory / 1024**3:.2f} GB")
            print(f"  Compute Capability: {torch.cuda.get_device_properties(i).major}.{torch.cuda.get_device_properties(i).minor}")
    else:
        print("❌ CUDA is not available! GPU inference will not work.")
        return False
    
    return True

def check_gpu_memory():
    """Check current GPU memory usage"""
    print_header("2. GPU Memory Usage")
    
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=index,name,memory.used,memory.total,utilization.gpu', '--format=csv,noheader'],
            capture_output=True,
            text=True,
            check=True
        )
        
        print("Current GPU Status:")
        print("GPU | Name | Memory Used | Memory Total | GPU Util")
        print("-" * 70)
        print(result.stdout.strip())
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running nvidia-smi: {e}")
        return False
    except FileNotFoundError:
        print("❌ nvidia-smi not found. Is NVIDIA driver installed?")
        return False
    
    return True

def check_snac_device():
    """Check SNAC decoder device configuration"""
    print_header("3. SNAC Decoder Configuration")
    
    snac_device_env = os.environ.get("SNAC_DEVICE", "not set")
    print(f"SNAC_DEVICE environment variable: {snac_device_env}")
    
    if snac_device_env == "not set":
        print("⚠️  WARNING: SNAC_DEVICE not set. Defaulting to CUDA if available.")
        print("   Recommendation: export SNAC_DEVICE=cuda")
    
    try:
        # Set SNAC_DEVICE for this test
        os.environ['SNAC_DEVICE'] = 'cuda'
        
        print("\nLoading SNAC decoder...")
        from orpheus_tts.decoder import model, snac_device
        
        print(f"✅ SNAC device: {snac_device}")
        
        # Check actual device of model parameters
        actual_device = next(model.parameters()).device
        print(f"✅ SNAC model loaded on: {actual_device}")
        
        if str(actual_device) == 'cpu':
            print("❌ WARNING: SNAC is on CPU! This will be very slow.")
            print("   Set SNAC_DEVICE=cuda and restart server.")
        else:
            print("✅ SNAC is correctly on GPU")
        
    except Exception as e:
        print(f"❌ Error loading SNAC: {e}")
        return False
    
    return True

def check_vllm_config():
    """Check vLLM configuration"""
    print_header("4. vLLM Configuration")
    
    try:
        import vllm
        print(f"vLLM version: {vllm.__version__}")
        
        if vllm.__version__ != "0.7.3":
            print(f"⚠️  WARNING: Expected vLLM 0.7.3, got {vllm.__version__}")
            print("   Recommendation: pip install vllm==0.7.3")
        else:
            print("✅ vLLM version is correct")
        
    except ImportError:
        print("❌ vLLM not installed!")
        return False
    
    # Check environment variables
    print("\nEnvironment Variables:")
    env_vars = {
        'MAX_MODEL_LEN': '2048',
        'GPU_MEMORY_UTILIZATION': '0.85',
        'SNAC_DEVICE': 'cuda',
        'MODEL_NAME': 'canopylabs/orpheus-tts-0.1-finetune-prod'
    }
    
    for var, recommended in env_vars.items():
        current = os.environ.get(var, 'not set')
        status = "✅" if current != 'not set' else "⚠️ "
        print(f"{status} {var}: {current} (recommended: {recommended})")
    
    return True

def check_orpheus_installation():
    """Check Orpheus TTS installation"""
    print_header("5. Orpheus TTS Installation")
    
    try:
        from orpheus_tts import OrpheusModel
        print("✅ orpheus_tts module found")
        
        # Check if it's the local version
        import orpheus_tts
        install_path = orpheus_tts.__file__
        print(f"Installation path: {install_path}")
        
        if 'orpheus_tts_pypi' in install_path:
            print("✅ Using local repository version (correct)")
        else:
            print("⚠️  Using PyPI version (may be outdated)")
            print("   Recommendation: pip uninstall orpheus-speech && cd orpheus_tts_pypi && pip install -e .")
        
    except ImportError as e:
        print(f"❌ orpheus_tts not installed: {e}")
        return False
    
    return True

def test_gpu_performance():
    """Quick GPU performance test"""
    print_header("6. GPU Performance Test")
    
    if not torch.cuda.is_available():
        print("❌ CUDA not available, skipping performance test")
        return False
    
    print("Running matrix multiplication benchmark...")
    
    # Warm up
    device = torch.device('cuda')
    a = torch.randn(1000, 1000, device=device)
    b = torch.randn(1000, 1000, device=device)
    _ = torch.matmul(a, b)
    torch.cuda.synchronize()
    
    # Benchmark
    iterations = 100
    start = time.time()
    
    for _ in range(iterations):
        c = torch.matmul(a, b)
    
    torch.cuda.synchronize()
    elapsed = time.time() - start
    
    tflops = (2 * 1000**3 * iterations) / (elapsed * 1e12)
    
    print(f"Matrix multiplication (1000x1000):")
    print(f"  Iterations: {iterations}")
    print(f"  Time: {elapsed:.3f}s")
    print(f"  Performance: {tflops:.2f} TFLOPS")
    
    # Expected performance for RTX A4500
    expected_tflops = 15  # Approximate for FP32
    
    if tflops < expected_tflops * 0.5:
        print(f"⚠️  WARNING: Performance is low (expected ~{expected_tflops} TFLOPS)")
        print("   Check for thermal throttling or other GPU processes")
    else:
        print(f"✅ GPU performance is good")
    
    return True

def check_running_processes():
    """Check for other GPU processes"""
    print_header("7. Running GPU Processes")
    
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-compute-apps=pid,process_name,used_memory', '--format=csv,noheader'],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout.strip():
            print("GPU processes:")
            print("PID | Process Name | Memory Used")
            print("-" * 70)
            print(result.stdout.strip())
        else:
            print("No GPU processes currently running")
            print("(This is expected if server is not running)")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking GPU processes: {e}")
        return False
    
    return True

def print_recommendations():
    """Print optimization recommendations"""
    print_header("Recommendations")
    
    print("""
Based on the diagnostics above, here are the recommended actions:

1. **Set Environment Variables** (if not already set):
   ```bash
   export MAX_MODEL_LEN=2048
   export GPU_MEMORY_UTILIZATION=0.85
   export SNAC_DEVICE=cuda
   ```

2. **Verify SNAC is on GPU**:
   - Check section 3 above
   - If SNAC is on CPU, set SNAC_DEVICE=cuda and restart

3. **Monitor GPU During Generation**:
   ```bash
   nvidia-smi dmon -s u -d 1
   ```
   - Run this in a separate terminal while making TTS requests
   - You should see 15-45% GPU utilization spikes

4. **Test Performance**:
   ```bash
   time curl "http://localhost:8080/tts?prompt=Hello%20world&voice=tara" --output test.wav
   ```
   - Should complete in 10-15 seconds for short prompts

5. **Check Server Logs**:
   - Look for "Avg generation throughput: X.X tokens/s"
   - Target: 50-70 tokens/s (up from 42 tokens/s)

For detailed optimization guide, see:
  runpod_deployment/RTX_A4500_OPTIMIZATION_GUIDE.md
""")

def main():
    """Run all diagnostic checks"""
    print("\n" + "="*70)
    print("  Orpheus TTS GPU Diagnostic Tool")
    print("  RTX A4500 Optimization")
    print("="*70)
    
    checks = [
        ("CUDA Availability", check_cuda_availability),
        ("GPU Memory", check_gpu_memory),
        ("SNAC Configuration", check_snac_device),
        ("vLLM Configuration", check_vllm_config),
        ("Orpheus Installation", check_orpheus_installation),
        ("GPU Performance", test_gpu_performance),
        ("Running Processes", check_running_processes),
    ]
    
    results = {}
    
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            results[name] = False
    
    # Summary
    print_header("Diagnostic Summary")
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✅ All checks passed! Your system is configured correctly.")
    else:
        print("\n⚠️  Some checks failed. Review the output above for details.")
    
    print_recommendations()
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

