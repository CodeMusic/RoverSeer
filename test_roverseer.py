#!/usr/bin/env python3
"""
Test script for RoverSeer API with Rainbow Driver integration
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_chat():
    """Test the chat endpoint with timer display"""
    print("Testing chat endpoint...")
    
    payload = {
        "model": "tinydolphin:1.1b",
        "messages": [
            {"role": "user", "content": "What is the capital of France? Give me a very short answer."}
        ],
        "system": "You are a helpful assistant. Keep answers extremely brief."
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    if response.ok:
        data = response.json()
        print(f"Success! Response: {data}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def test_tts():
    """Test the TTS endpoint"""
    print("\nTesting TTS endpoint...")
    
    payload = {
        "text": "Hello, this is RoverSeer speaking!",
        "voice": "en_GB-jarvis"
    }
    
    response = requests.post(f"{BASE_URL}/say", json=payload)
    if response.ok:
        print(f"Success! {response.json()}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def test_sensor_status():
    """Test the home page to check sensor data"""
    print("\nChecking sensor data on home page...")
    
    response = requests.get(f"{BASE_URL}/")
    if response.ok:
        print("Home page loaded successfully!")
        # You could parse the HTML here to extract sensor data if needed
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    print("RoverSeer API Test Suite")
    print("========================")
    
    # Give the API a moment to be ready
    time.sleep(1)
    
    try:
        test_chat()
        time.sleep(2)  # Wait between tests
        test_tts()
        test_sensor_status()
    except Exception as e:
        print(f"Test failed with error: {e}")
    
    print("\nTests complete!") 