#!/usr/bin/env python3
"""
Model Size Comparison for Saaransh Use Cases

Analyzes whether 8B or 3B model is better for your specific application.
"""

import asyncio
import time
from app.accessors.llm.local_llama_accessor import LocalLlamaAccessor


async def test_saaransh_use_cases(model_name):
    """Test model performance on actual Saaransh use cases"""
    
    print(f"\n🧪 Testing {model_name} for Saaransh Use Cases")
    print("=" * 60)
    
    accessor = LocalLlamaAccessor()
    # Override model for testing
    accessor.model = model_name
    
    test_cases = [
        {
            "name": "Task Summarization",
            "content": """
            Project: Website Redesign
            Tasks:
            - Design new homepage layout with modern UI components
            - Implement responsive navigation menu for mobile devices  
            - Optimize images and assets for faster loading times
            - Conduct user testing sessions with 10 participants
            - Update brand colors and typography across all pages
            - Integrate new contact form with validation
            """,
            "prompt": "Summarize this project and its key tasks in 2-3 sentences.",
            "system": "You are an expert project manager. Provide clear, concise summaries."
        },
        {
            "name": "Comment Enhancement",
            "content": "Task: Fix login bug",
            "prompt": "Enhance this comment: 'looks good'",
            "system": "You help improve task comments to be more specific and helpful."
        },
        {
            "name": "Quick Q&A",
            "content": "",
            "prompt": "What's the status of the website redesign project?",
            "system": "You are a helpful assistant for project management questions."
        },
        {
            "name": "Content Analysis",
            "content": """
            Bug Report: Users can't log in on mobile devices
            Steps to reproduce:
            1. Open app on mobile browser
            2. Enter valid credentials
            3. Tap login button
            4. Page refreshes but user not logged in
            
            Expected: User should be logged in
            Actual: Login fails silently
            """,
            "prompt": "Analyze this bug report and suggest priority level and next steps.",
            "system": "You are a technical analyst. Be concise and actionable."
        }
    ]
    
    results = []
    
    try:
        for test_case in test_cases:
            print(f"\n🔄 Testing: {test_case['name']}")
            
            start_time = time.time()
            
            try:
                response = await accessor.get_response(
                    model=model_name,
                    content=test_case['content'],
                    user_prompt=test_case['prompt'],
                    system_prompt=test_case['system']
                )
                
                duration = time.time() - start_time
                
                # Analyze response quality
                word_count = len(response.split())
                is_relevant = any(keyword in response.lower() for keyword in 
                                ['project', 'task', 'website', 'login', 'bug', 'user'])
                
                print(f"⏱️  Time: {duration:.2f}s")
                print(f"📝 Response: {word_count} words")
                print(f"🎯 Relevant: {'Yes' if is_relevant else 'No'}")
                print(f"💬 Preview: {response[:100]}...")
                
                results.append({
                    "use_case": test_case['name'],
                    "duration": duration,
                    "word_count": word_count,
                    "relevant": is_relevant,
                    "response": response,
                    "quality_score": min(10, word_count / 10) if is_relevant else 0
                })
                
            except Exception as e:
                print(f"❌ Failed: {e}")
                results.append({
                    "use_case": test_case['name'],
                    "error": str(e)
                })
        
        return results
        
    finally:
        await accessor.close()


def analyze_model_suitability(results_8b, results_3b):
    """Compare models and recommend best choice"""
    
    print("\n📊 Model Comparison Analysis")
    print("=" * 60)
    
    if not results_8b or not results_3b:
        print("⚠️  Cannot compare - missing test results")
        return
    
    # Calculate averages
    avg_time_8b = sum(r.get('duration', 0) for r in results_8b if 'duration' in r) / len([r for r in results_8b if 'duration' in r])
    avg_time_3b = sum(r.get('duration', 0) for r in results_3b if 'duration' in r) / len([r for r in results_3b if 'duration' in r])
    
    avg_quality_8b = sum(r.get('quality_score', 0) for r in results_8b if 'quality_score' in r) / len([r for r in results_8b if 'quality_score' in r])
    avg_quality_3b = sum(r.get('quality_score', 0) for r in results_3b if 'quality_score' in r) / len([r for r in results_3b if 'quality_score' in r])
    
    print(f"📈 Performance Comparison:")
    print(f"   8B Model: {avg_time_8b:.2f}s avg, Quality: {avg_quality_8b:.1f}/10")
    print(f"   3B Model: {avg_time_3b:.2f}s avg, Quality: {avg_quality_3b:.1f}/10")
    
    # Speed improvement
    speed_improvement = ((avg_time_8b - avg_time_3b) / avg_time_8b) * 100
    print(f"   Speed Improvement (3B): {speed_improvement:.1f}% faster")
    
    # Quality difference
    quality_diff = avg_quality_8b - avg_quality_3b
    print(f"   Quality Difference: {quality_diff:.1f} points")
    
    # Recommendation
    print(f"\n🎯 Recommendation for Saaransh:")
    
    if avg_time_8b > 15:  # Very slow
        print("   🔴 SWITCH TO 3B: 8B model too slow for production use")
        recommendation = "3B"
    elif avg_time_8b > 8 and speed_improvement > 50:  # Moderate speed, big improvement
        print("   🟡 CONSIDER 3B: Significant speed improvement with acceptable quality")
        recommendation = "3B"
    elif quality_diff > 2:  # Much better quality
        print("   🟢 KEEP 8B: Quality improvement justifies slower speed")
        recommendation = "8B"
    else:
        print("   🟡 EITHER: Both models suitable, choose based on priority")
        recommendation = "Either"
    
    return {
        "recommendation": recommendation,
        "speed_improvement": speed_improvement,
        "quality_difference": quality_diff,
        "avg_time_8b": avg_time_8b,
        "avg_time_3b": avg_time_3b
    }


async def main():
    """Run comprehensive model comparison"""
    
    print("🚀 Saaransh Model Suitability Analysis")
    print("=" * 60)
    
    # Check available models
    accessor = LocalLlamaAccessor()
    try:
        models = await accessor.get_available_models()
        print(f"📋 Available models: {models}")
        
        has_8b = any("8b" in model.lower() for model in models)
        has_3b = any("3b" in model.lower() for model in models)
        
        if not has_8b:
            print("⚠️  8B model not found. Install with: ollama pull llama3.1:8b")
        if not has_3b:
            print("⚠️  3B model not found. Install with: ollama pull llama3.1:3b")
            
    finally:
        await accessor.close()
    
    results_8b = None
    results_3b = None
    
    # Test 8B model if available
    if has_8b:
        results_8b = await test_saaransh_use_cases("llama3.1:8b")
    
    # Test 3B model if available  
    if has_3b:
        results_3b = await test_saaransh_use_cases("llama3.1:3b")
    
    # Compare results
    if results_8b and results_3b:
        analysis = analyze_model_suitability(results_8b, results_3b)
        
        print(f"\n✅ Analysis Complete!")
        print(f"Recommended model: {analysis['recommendation']}")
        
    elif results_8b:
        avg_time = sum(r.get('duration', 0) for r in results_8b if 'duration' in r) / len([r for r in results_8b if 'duration' in r])
        print(f"\n📊 8B Model Analysis:")
        print(f"Average response time: {avg_time:.2f}s")
        
        if avg_time > 15:
            print("🔴 RECOMMENDATION: Too slow for production. Consider 3B model.")
        elif avg_time > 8:
            print("🟡 RECOMMENDATION: Acceptable but could be faster. Test 3B model.")
        else:
            print("🟢 RECOMMENDATION: Good performance for production use.")


if __name__ == "__main__":
    asyncio.run(main())