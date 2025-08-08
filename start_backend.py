#!/usr/bin/env python3
"""
AI Assistant Backend Startup Script
"""

import os
import sys
import json
from pathlib import Path

def check_keys_file():
    """Check if keys.txt exists and has valid format"""
    keys_file = Path("keys.txt")
    
    if not keys_file.exists():
        print("❌ keys.txt not found!")
        print("\nPlease create a keys.txt file with your API configuration:")
        print("""
{
    "API_KEY": "your-api-key-here",
    "AI_Agent_URL": "https://your-ai-agent-url",
    "AI_Agent_Stream_URL": "https://your-stream-url"
}
        """)
        return False
    
    try:
        with open(keys_file, 'r') as f:
            config = json.load(f)
        
        required_keys = ["API_KEY", "AI_Agent_URL", "AI_Agent_Stream_URL"]
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            print(f"❌ Missing required keys in keys.txt: {missing_keys}")
            return False
        
        if config["API_KEY"] == "your-api-key-here":
            print("❌ Please update your API key in keys.txt")
            return False
            
        print("✅ keys.txt configuration looks good!")
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON format in keys.txt")
        return False
    except Exception as e:
        print(f"❌ Error reading keys.txt: {e}")
        return False

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "langchain",
        "faiss",
        "sentence_transformers",
        "pymupdf"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {missing_packages}")
        print("\nPlease install them with:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed!")
    return True

def create_temp_folder():
    """Create temporary uploads folder"""
    temp_folder = Path("./tmp_uploads")
    temp_folder.mkdir(exist_ok=True)
    print("✅ Temporary uploads folder ready!")

def main():
    print("🚀 Starting AI Assistant Backend...")
    print("=" * 50)
    
    # Check configuration
    if not check_keys_file():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create temp folder
    create_temp_folder()
    
    print("\n" + "=" * 50)
    print("✅ All checks passed! Starting server...")
    print("\n🌐 Server will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    # Import and run the server
    try:
        from api_server import app
        import uvicorn
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
