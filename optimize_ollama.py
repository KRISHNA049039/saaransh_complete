#!/usr/bin/env python3
"""
Ollama Performance Optimization Script

This script helps optimize your Ollama setup for better performance with the Saaransh backend.
"""

import asyncio
import httpx
import time
import psutil
import os
from app.accessors.llm.local_llama_accessor import LocalLlamaAccessor


async def check_system_resources():
    """Check system resources and provide recommendations"""
    
    print("🔍 System Resource Analysis")
    print("=" * 50)
    
    # Memory check
    memory = psutil.virtual_memory()
    print(f"💾 Total RAM: {memory.total / (1024**3):.1f} GB")
    print(f"💾 Available RAM: {memory.available / (1024**3):.1f} GB")
    print(f"💾 RAM Usage: {memory.percent}%")
    
    if memory.total < 8 * (1024**3):  # Less than 8GB
        print("⚠️  WARNING: Less than 8GB RAM detected. Consider upgrading for better performance.")
    elif memory.total < 16 * (1024**3):  # Less than 16GB
        print("ℹ️  INFO: 8-16GB RAM detected. Performance may be limited with large models.")
    else:
        print("✅ GOOD: 16GB+ RAM detected. Optimal for local LLM inference.")
    
    # CPU check
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    print(f"\n🖥️  CPU Cores: {cpu_count}")
    if cpu_freq:
        print(f"🖥️  CPU Frequency: {cpu_freq.current:.0f} MHz")
    
    # Disk check
    disk = psutil.disk_usage('/')
    print(f"\n💽 Disk Space: {disk.free / (1024**3):.1f} GB free")
    
    return {
        "ram_gb": memory.total / (1024**3),
        "ram_available_gb": memory.available / (1024**3),
        "cpu_cores": cpu_count,
        "disk_free_gb": disk.free / (1024**3)
    }


async def test_ollama_performance():
    """Test current Ollama performance"""
    
    print("\n🧪 Ollama Performance Test")
    print("=" * 50)
    
    try:
        accessor = LocalLlamaAccessor()
        
        # Health check
        print("🏥 Testing Ollama connectivity...")
        start_time = time.time()
        healthy = await accessor.health_check()
        health_time = time.time() - start_time
        
        if not healthy:
            print("❌ Ollama is not running or not accessible")
            print("💡 Try running: ollama serve")
            return None
        
        print(f"✅ Ollama is healthy (response time: {health_time:.2f}s)")
        
        # Get available models
        models = await accessor.get_available_models()
        print(f"📋 Available models: {models}")
        
        # Performance tests
        tests = [
            ("Short response", "Say hello", "Be brief"),
            ("Medium response", "Explain AI in 2 sentences", "Be concise"),
        ]
        
        results = []
        
        for test_name, prompt, system in tests:
            print(f"\n🔄 Testing: {test_name}")
            start_time = time.time()
            
            try:
                response = await accessor.get_response(
                    model="llama3.1:8b",
                    content="",
                    user_prompt=prompt,
                    system_prompt=system
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                word_count = len(response.split())
                chars_per_sec = len(response) / duration
                words_per_sec = word_count / duration
                
                print(f"⏱️  Duration: {duration:.2f}s")
                print(f"📝 Response: {len(response)} chars, {word_count} words")
                print(f"🚀 Speed: {chars_per_sec:.1f} chars/sec, {words_per_sec:.1f} words/sec")
                
                results.append({
                    "test": test_name,
                    "duration": duration,
                    "response_length": len(response),
                    "words": word_count,
                    "chars_per_sec": chars_per_sec,
                    "words_per_sec": words_per_sec
                })
                
            except Exception as e:
                print(f"❌ Test failed: {e}")
                results.append({
                    "test": test_name,
                    "error": str(e)
                })
        
        await accessor.close()
        return results
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return None


def generate_optimization_recommendations(system_info, performance_results):
    """Generate personalized optimization recommendations"""
    
    print("\n💡 Optimization Recommendations")
    print("=" * 50)
    
    recommendations = []
    
    # RAM-based recommendations
    if system_info["ram_gb"] < 8:
        recommendations.append("🔴 CRITICAL: Upgrade to at least 8GB RAM")
    elif system_info["ram_gb"] < 16:
        recommendations.append("🟡 RECOMMENDED: Upgrade to 16GB RAM for better performance")
        recommendations.append("🔧 Use smaller model: ollama pull llama3.1:3b")
    
    # Performance-based recommendations
    if performance_results:
        avg_time = sum(r.get("duration", 0) for r in performance_results if "duration" in r) / len([r for r in performance_results if "duration" in r])
        
        if avg_time > 15:
            recommendations.extend([
                "🔧 Reduce max_tokens in .env (set LOCAL_LLM_MAX_TOKENS=256)",
                "🔧 Use smaller context window (set LOCAL_LLM_CONTEXT_LENGTH=2048)",
                "🔧 Consider switching to llama3.1:3b model for faster responses"
            ])
        elif avg_time > 8:
            recommendations.extend([
                "🔧 Optimize max_tokens (set LOCAL_LLM_MAX_TOKENS=512)",
                "🔧 Lower temperature for faster responses (set LOCAL_LLM_TEMPERATURE=0.3)"
            ])
        else:
            recommendations.append("✅ Performance is good! No major optimizations needed.")
    
    # General recommendations
    recommendations.extend([
        "🔧 Close unnecessary applications to free RAM",
        "🔧 Use SSD storage for faster model loading",
        "🔧 Keep Ollama running to avoid cold starts",
        "🔧 Consider GPU acceleration if available"
    ])
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    return recommendations


def generate_optimized_env_config(system_info):
    """Generate optimized .env configuration"""
    
    print("\n⚙️  Optimized Configuration")
    print("=" * 50)
    
    # Determine optimal settings based on system
    if system_info["ram_gb"] < 8:
        max_tokens = 128
        context_length = 1024
        model = "llama3.1:3b"  # Smaller model
    elif system_info["ram_gb"] < 16:
        max_tokens = 256
        context_length = 2048
        model = "llama3.1:8b"
    else:
        max_tokens = 512
        context_length = 4096
        model = "llama3.1:8b"
    
    config = f"""
# Optimized Local LLM Configuration
LOCAL_LLM_ENABLED=true
LOCAL_LLM_HOST=localhost
LOCAL_LLM_PORT=11434
LOCAL_LLM_MODEL={model}
LOCAL_LLM_TIMEOUT=120
LOCAL_LLM_TEMPERATURE=0.7
LOCAL_LLM_CONTEXT_LENGTH={context_length}
LOCAL_LLM_MAX_TOKENS={max_tokens}

# Performance optimizations
LOCAL_LLM_BATCH_SIZE=1
LOCAL_LLM_THREADS={min(system_info["cpu_cores"], 8)}
"""
    
    print("Add this to your .env file:")
    print(config)
    
    return config


async def main():
    """Main optimization workflow"""
    
    print("🚀 Saaransh Ollama Performance Optimizer")
    print("=" * 60)
    
    # Step 1: Check system resources
    system_info = await check_system_resources()
    
    # Step 2: Test current performance
    performance_results = await test_ollama_performance()
    
    # Step 3: Generate recommendations
    recommendations = generate_optimization_recommendations(system_info, performance_results)
    
    # Step 4: Generate optimized config
    optimized_config = generate_optimized_env_config(system_info)
    
    print("\n🎯 Summary")
    print("=" * 50)
    print(f"System RAM: {system_info['ram_gb']:.1f} GB")
    print(f"CPU Cores: {system_info['cpu_cores']}")
    
    if performance_results:
        avg_time = sum(r.get("duration", 0) for r in performance_results if "duration" in r) / len([r for r in performance_results if "duration" in r])
        print(f"Average Response Time: {avg_time:.2f}s")
        
        if avg_time < 5:
            print("🟢 Performance: Excellent")
        elif avg_time < 10:
            print("🟡 Performance: Good")
        else:
            print("🔴 Performance: Needs Optimization")
    
    print("\n✅ Optimization complete! Apply the recommended settings and restart your server.")


if __name__ == "__main__":
    asyncio.run(main())