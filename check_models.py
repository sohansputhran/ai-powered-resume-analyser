#!/usr/bin/env python3
"""
Script to check available Gemini models for your API key
Run this to see which models you can use
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

def check_available_models():
    """Check which Gemini models are available with your API key"""
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in environment variables")
        print("Please add your API key to the .env file")
        return
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        print("🔍 Checking available Gemini models...\n")
        
        # List all available models
        models = genai.list_models()
        
        print("✅ Available models:")
        print("-" * 50)
        
        for model in models:
            # Check if model supports generateContent
            if 'generateContent' in model.supported_generation_methods:
                print(f"📋 Model: {model.name}")
                print(f"   Display Name: {model.display_name}")
                print(f"   Description: {model.description}")
                print(f"   Input Token Limit: {model.input_token_limit}")
                print(f"   Output Token Limit: {model.output_token_limit}")
                print("-" * 50)
        
        # Test a simple generation with the recommended model
        print("\n🧪 Testing model connection...")
        
        # Try different model names in order of preference
        test_models = [
            "gemini-1.5-flash",
            "gemini-1.5-pro", 
            "gemini-pro",
            "models/gemini-1.5-flash",
            "models/gemini-1.5-pro",
            "models/gemini-pro"
        ]
        
        working_model = None
        
        for model_name in test_models:
            try:
                print(f"   Testing {model_name}...")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Say 'Hello, this model is working!'")
                
                if response.text:
                    print(f"   ✅ {model_name} is working!")
                    print(f"   Response: {response.text}")
                    working_model = model_name
                    break
                    
            except Exception as e:
                print(f"   ❌ {model_name} failed: {str(e)}")
                continue
        
        if working_model:
            print(f"\n🎉 Recommended model to use: {working_model}")
            print(f"Update your config to use: {working_model}")
        else:
            print("\n❌ No working models found. Please check your API key.")
            
    except Exception as e:
        print(f"❌ Error checking models: {str(e)}")
        print("\nPossible solutions:")
        print("1. Check if your API key is valid")
        print("2. Ensure you have internet connection")
        print("3. Verify your API key has the necessary permissions")

if __name__ == "__main__":
    check_available_models()