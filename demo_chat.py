#!/usr/bin/env python3
"""
Demo script for AI Assistant Chatbot
Tests the API endpoints and demonstrates functionality
"""

import requests
import json
import time
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
SESSION_ID = "demo_session_123"

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_chat():
    """Test the chat endpoint"""
    print("\n💬 Testing chat endpoint...")
    
    # Test basic chat
    chat_data = {
        "message": "Hello! I'm testing the AI assistant. Can you tell me about yourself?",
        "session_id": SESSION_ID
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/chat", json=chat_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat response received:")
            print(f"   Content: {data['content'][:100]}...")
            print(f"   Session ID: {data['session_id']}")
            print(f"   Success: {data['success']}")
            return True
        else:
            print(f"❌ Chat failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False

def test_chat_history():
    """Test chat history endpoint"""
    print("\n📚 Testing chat history...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/chat/history?session_id={SESSION_ID}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat history retrieved:")
            print(f"   Messages: {len(data['messages'])}")
            for i, msg in enumerate(data['messages'][-2:], 1):  # Show last 2 messages
                print(f"   {i}. {msg['role']}: {msg['content'][:50]}...")
            return True
        else:
            print(f"❌ Chat history failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Chat history error: {e}")
        return False

def test_contextual_chat():
    """Test contextual chat with follow-up questions"""
    print("\n🧠 Testing contextual chat...")
    
    messages = [
        "My name is Alice and I love reading science fiction books.",
        "What's my name and what do I like to read?",
        "Can you recommend a good science fiction book for me?"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n   Message {i}: {message}")
        
        chat_data = {
            "message": message,
            "session_id": SESSION_ID
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/chat", json=chat_data)
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {data['content'][:100]}...")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
        
        time.sleep(1)  # Small delay between messages
    
    return True

def test_file_upload():
    """Test file upload functionality"""
    print("\n📄 Testing file upload...")
    
    # Create a simple test PDF (you would need a real PDF file for this)
    test_file_path = Path("test_document.pdf")
    
    if not test_file_path.exists():
        print("   ⚠️  No test PDF found. Skipping file upload test.")
        print("   Create a test_document.pdf file to test this functionality.")
        return True
    
    try:
        with open(test_file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{API_BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ File uploaded: {data['filename']}")
            
            # Test asking a question about the uploaded file
            chat_data = {
                "message": "What is this document about?",
                "session_id": SESSION_ID,
                "filename": data['filename']
            }
            
            response = requests.post(f"{API_BASE_URL}/chat", json=chat_data)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Document question answered: {data['content'][:100]}...")
                if data.get('sources'):
                    print(f"   📚 Sources found: {len(data['sources'])}")
            
            return True
        else:
            print(f"   ❌ File upload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ File upload error: {e}")
        return False

def test_streaming():
    """Test streaming chat endpoint"""
    print("\n🌊 Testing streaming chat...")
    
    chat_data = {
        "message": "Tell me a short story about a robot learning to paint.",
        "session_id": SESSION_ID
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat/stream", 
            json=chat_data,
            stream=True
        )
        
        if response.status_code == 200:
            print("   ✅ Streaming response:")
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        if data_str == '[DONE]':
                            break
                        try:
                            data = json.loads(data_str)
                            if 'content' in data:
                                chunk = data['content']
                                full_response += chunk
                                print(f"   {chunk}", end='', flush=True)
                        except json.JSONDecodeError:
                            continue
            
            print(f"\n   ✅ Full response length: {len(full_response)} characters")
            return True
        else:
            print(f"   ❌ Streaming failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Streaming error: {e}")
        return False

def cleanup():
    """Clean up demo session"""
    print("\n🧹 Cleaning up demo session...")
    
    try:
        response = requests.post(f"{API_BASE_URL}/chat/clear", json={"session_id": SESSION_ID})
        if response.status_code == 200:
            print("   ✅ Demo session cleared")
        else:
            print(f"   ⚠️  Failed to clear session: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Cleanup error: {e}")

def main():
    print("🤖 AI Assistant Chatbot Demo")
    print("=" * 50)
    
    # Check if server is running
    if not test_health():
        print("\n❌ Server is not running. Please start the backend first:")
        print("   python start_backend.py")
        return
    
    # Run tests
    tests = [
        ("Basic Chat", test_chat),
        ("Chat History", test_chat_history),
        ("Contextual Chat", test_contextual_chat),
        ("File Upload", test_file_upload),
        ("Streaming Chat", test_streaming),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    # Cleanup
    cleanup()
    
    # Summary
    print(f"\n{'='*50}")
    print(f"📊 Demo Results: {passed}/{total} tests passed")
    if passed == total:
        print("🎉 All tests passed! Your AI Assistant is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the server logs for details.")
    print("=" * 50)

if __name__ == "__main__":
    main()
