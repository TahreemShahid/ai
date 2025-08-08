#!/usr/bin/env python3
"""
Simple script to run the backend server
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'langchain',
        'langchain_community',
        'langchain_huggingface',
        'pymupdf',
        'faiss',
        'sentence_transformers'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Missing required packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\n📦 Install missing packages with:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_custom_llm():
    """Check if custom LLM file exists"""
    if not os.path.exists('custom_langchain.py'):
        print("⚠️  custom_langchain.py not found")
        print("   The API will work with mock responses until you add your custom LLM")
        return False
    
    print("✅ custom_langchain.py found")
    return True

def check_keys():
    """Check if keys.txt exists"""
    if not os.path.exists('keys.txt'):
        print("⚠️  keys.txt not found")
        print("   Copy keys.txt.example to keys.txt and add your API keys")
        print("   The API will work with mock responses until configured")
        return False
    
    print("✅ keys.txt found")
    return True

def main():
    print("🚀 Starting your app's Backend Server")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check optional files
    check_custom_llm()
    check_keys()
    
    print("\n🌐 Starting server on http://localhost:8000")
    print("📚 API docs available at http://localhost:8000/docs")
    print("🔄 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Run the server
        subprocess.run([
            sys.executable, 
            "api_server.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()