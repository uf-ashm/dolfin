#!/usr/bin/env python3
"""
Test script to verify OpenAI configuration and API connectivity.
Run this script to check if your setup is working correctly.
"""

import os
import sys
from config import config
from openai_client import openai_client

def test_configuration():
    """Test the application configuration."""
    print("🔧 Testing Configuration...")
    print("=" * 50)
    
    # Test API key
    is_valid, error = config.validate_openai_config()
    print(f"API Key Status: {config.get_status_message()}")
    
    if not is_valid:
        print(f"❌ Configuration Error: {error}")
        return False
    
    print("✅ Configuration is valid")
    return True

def test_api_connection():
    """Test API connection with a simple request."""
    print("\n🌐 Testing API Connection...")
    print("=" * 50)
    
    try:
        # Simple test message
        test_messages = [{"role": "user", "content": "Say 'Hello, API is working!'"}]
        
        response = openai_client.safe_chat_completion(
            messages=test_messages,
            fallback_info="Test fallback response",
            question="API connection test"
        )
        
        if "⚠️" in response or "quota" in response.lower() or "exceeded" in response.lower():
            print("⚠️ API Error Detected:")
            print(response)
            return False
        else:
            print("✅ API Connection Successful!")
            print(f"Response: {response}")
            return True
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 OpenAI API Configuration Test")
    print("=" * 50)
    
    # Test configuration
    config_ok = test_configuration()
    
    if not config_ok:
        print("\n❌ Configuration test failed. Please fix the issues above.")
        sys.exit(1)
    
    # Test API connection
    api_ok = test_api_connection()
    
    if api_ok:
        print("\n🎉 All tests passed! Your setup is ready to use.")
    else:
        print("\n⚠️ API connection test failed. Check your quota and billing.")
        print("The application will still work with fallback responses.")

if __name__ == "__main__":
    main()
