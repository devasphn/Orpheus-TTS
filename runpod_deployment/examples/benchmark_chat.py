#!/usr/bin/env python3
"""
Performance Benchmarking Tool for Conversational AI Pipeline
Measures end-to-end latency and throughput
"""

import requests
import json
import time
import statistics
from pathlib import Path

SERVER_URL = "http://localhost:8080"

def benchmark_chat(message, voice="tara", num_runs=3):
    """
    Benchmark the /chat endpoint
    
    Args:
        message: Test message
        voice: Voice name
        num_runs: Number of test runs
    
    Returns:
        dict with benchmark results
    """
    print(f"\n{'='*70}")
    print(f"BENCHMARKING: {message[:50]}...")
    print(f"Voice: {voice}")
    print(f"Runs: {num_runs}")
    print(f"{'='*70}")
    
    results = {
        'message': message,
        'voice': voice,
        'runs': [],
        'avg_total_time': 0,
        'avg_file_size': 0,
        'avg_throughput': 0
    }
    
    for run in range(num_runs):
        print(f"\nRun {run + 1}/{num_runs}...")
        
        payload = {
            "message": message,
            "voice": voice
        }
        
        start_time = time.time()
        first_chunk_time = None
        
        try:
            response = requests.post(
                f"{SERVER_URL}/chat",
                json=payload,
                stream=True,
                timeout=120
            )
            
            if response.status_code != 200:
                print(f"❌ Error: Status {response.status_code}")
                continue
            
            # Save to temp file
            temp_file = Path(f"benchmark_temp_{run}.wav")
            chunk_count = 0
            
            with open(temp_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        if first_chunk_time is None:
                            first_chunk_time = time.time()
                        f.write(chunk)
                        chunk_count += 1
            
            end_time = time.time()
            
            # Calculate metrics
            total_time = end_time - start_time
            time_to_first_chunk = first_chunk_time - start_time if first_chunk_time else 0
            file_size = temp_file.stat().st_size
            
            # Estimate tokens (rough approximation)
            # Assume ~7 tokens per audio chunk, ~110 bytes per chunk
            estimated_chunks = file_size / 110
            estimated_tokens = estimated_chunks * 7
            throughput = estimated_tokens / total_time if total_time > 0 else 0
            
            run_result = {
                'total_time': total_time,
                'time_to_first_chunk': time_to_first_chunk,
                'file_size': file_size,
                'chunk_count': chunk_count,
                'estimated_tokens': estimated_tokens,
                'throughput': throughput
            }
            
            results['runs'].append(run_result)
            
            print(f"  Total time: {total_time:.2f}s")
            print(f"  Time to first chunk: {time_to_first_chunk:.3f}s")
            print(f"  File size: {file_size / 1024:.1f} KB")
            print(f"  Chunks: {chunk_count}")
            print(f"  Estimated tokens: {estimated_tokens:.0f}")
            print(f"  Throughput: {throughput:.1f} tok/s")
            
            # Clean up temp file
            temp_file.unlink()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    
    # Calculate averages
    if results['runs']:
        results['avg_total_time'] = statistics.mean([r['total_time'] for r in results['runs']])
        results['avg_time_to_first_chunk'] = statistics.mean([r['time_to_first_chunk'] for r in results['runs']])
        results['avg_file_size'] = statistics.mean([r['file_size'] for r in results['runs']])
        results['avg_throughput'] = statistics.mean([r['throughput'] for r in results['runs']])
        
        if len(results['runs']) > 1:
            results['std_total_time'] = statistics.stdev([r['total_time'] for r in results['runs']])
            results['std_throughput'] = statistics.stdev([r['throughput'] for r in results['runs']])
    
    return results

def print_benchmark_summary(results):
    """Print formatted benchmark summary"""
    print(f"\n{'='*70}")
    print("BENCHMARK SUMMARY")
    print(f"{'='*70}")
    print(f"Message: {results['message'][:50]}...")
    print(f"Voice: {results['voice']}")
    print(f"Successful runs: {len(results['runs'])}")
    print()
    
    if results['runs']:
        print(f"Average total time:        {results['avg_total_time']:.2f}s")
        print(f"Average time to 1st chunk: {results['avg_time_to_first_chunk']:.3f}s")
        print(f"Average file size:         {results['avg_file_size'] / 1024:.1f} KB")
        print(f"Average throughput:        {results['avg_throughput']:.1f} tok/s")
        
        if 'std_total_time' in results:
            print(f"\nStandard deviation:")
            print(f"  Total time: ±{results['std_total_time']:.2f}s")
            print(f"  Throughput: ±{results['std_throughput']:.1f} tok/s")
    else:
        print("❌ No successful runs")
    
    print(f"{'='*70}\n")

def run_comprehensive_benchmark():
    """Run comprehensive benchmark with different message lengths"""
    print("\n" + "="*70)
    print("COMPREHENSIVE BENCHMARK")
    print("="*70)
    
    test_cases = [
        ("Short", "Hello, how are you?"),
        ("Medium", "Can you explain what artificial intelligence is and how it works?"),
        ("Long", "I'm interested in learning about the history of space exploration. Can you tell me about the major milestones, from the first satellites to the moon landing and beyond?")
    ]
    
    all_results = []
    
    for name, message in test_cases:
        print(f"\n{'='*70}")
        print(f"TEST CASE: {name}")
        print(f"{'='*70}")
        
        results = benchmark_chat(message, voice="tara", num_runs=3)
        print_benchmark_summary(results)
        all_results.append((name, results))
        
        time.sleep(2)  # Brief pause between test cases
    
    # Print comparison table
    print("\n" + "="*70)
    print("COMPARISON TABLE")
    print("="*70)
    print(f"{'Test Case':<15} {'Avg Time':<12} {'TTFC':<12} {'Throughput':<15}")
    print("-" * 70)
    
    for name, results in all_results:
        if results['runs']:
            print(f"{name:<15} {results['avg_total_time']:>10.2f}s  {results['avg_time_to_first_chunk']:>10.3f}s  {results['avg_throughput']:>12.1f} tok/s")
    
    print("="*70)
    print("\nTTFC = Time To First Chunk")
    print()

def benchmark_llm_only():
    """Benchmark LLM text generation (no TTS)"""
    print("\n" + "="*70)
    print("LLM-ONLY BENCHMARK (Text Stream)")
    print("="*70)
    
    message = "Explain quantum computing in simple terms."
    
    print(f"\nMessage: {message}")
    print("Generating text response...\n")
    
    payload = {
        "message": message,
        "stream_text": True
    }
    
    start_time = time.time()
    first_token_time = None
    token_count = 0
    
    try:
        response = requests.post(
            f"{SERVER_URL}/chat",
            json=payload,
            stream=True,
            timeout=60
        )
        
        full_text = ""
        for chunk in response.iter_content(chunk_size=1):
            if chunk:
                if first_token_time is None:
                    first_token_time = time.time()
                
                text = chunk.decode('utf-8')
                print(text, end="", flush=True)
                full_text += text
                token_count += 1
        
        end_time = time.time()
        
        total_time = end_time - start_time
        ttft = first_token_time - start_time if first_token_time else 0
        throughput = token_count / total_time if total_time > 0 else 0
        
        print(f"\n\n{'='*70}")
        print("LLM BENCHMARK RESULTS")
        print(f"{'='*70}")
        print(f"Total time:           {total_time:.2f}s")
        print(f"Time to first token:  {ttft:.3f}s")
        print(f"Characters generated: {token_count}")
        print(f"Throughput:           {throughput:.1f} char/s")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

def main():
    """Main function"""
    print("\n" + "="*70)
    print("CONVERSATIONAL AI PERFORMANCE BENCHMARK")
    print("="*70)
    print("\nBenchmark options:")
    print("1. Quick benchmark (single message)")
    print("2. Comprehensive benchmark (short/medium/long)")
    print("3. LLM-only benchmark (text stream)")
    print("4. Custom message benchmark")
    print("0. Exit")
    
    while True:
        choice = input("\nSelect benchmark (0-4): ").strip()
        
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            results = benchmark_chat("Hello, how are you?", num_runs=3)
            print_benchmark_summary(results)
        elif choice == "2":
            run_comprehensive_benchmark()
        elif choice == "3":
            benchmark_llm_only()
        elif choice == "4":
            message = input("Enter message: ")
            voice = input("Enter voice (default: tara): ").strip() or "tara"
            num_runs = int(input("Number of runs (default: 3): ").strip() or "3")
            results = benchmark_chat(message, voice=voice, num_runs=num_runs)
            print_benchmark_summary(results)
        else:
            print("Invalid choice. Please select 0-4.")

if __name__ == "__main__":
    main()

