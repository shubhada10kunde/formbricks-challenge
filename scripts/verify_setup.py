#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path

def check_docker():
    try:
        result = subprocess.run(["docker", "--version"], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def check_python_packages():
    required = ["click", "requests", "docker", "ollama", "rich"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    return missing

def check_ollama():
    """Check if Ollama is running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            return True
        return False
    except:
        return False

def check_env_file():
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            content = f.read()
            # Check for Ollama config instead of OpenAI
            return "OLLAMA_URL=" in content and "FORMBRICKS_API_KEY=" in content
    return False

def main():
    print("🔍 Verifying setup...")
    
    # Check Docker
    if check_docker():
        print("✅ Docker is installed")
    else:
        print("❌ Docker not found")
        print("   Install from: https://www.docker.com/products/docker-desktop/")
    
    # Check Python packages
    missing = check_python_packages()
    if not missing:
        print("✅ All Python packages installed")
    else:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("   Install with: pip install -r requirements.txt")
    
    # Check Ollama
    if check_ollama():
        print("✅ Ollama is running")
    else:
        print("❌ Ollama not running")
        print("   Install from: https://ollama.com/")
        print("   Then run: ollama serve")
    
    # Check .env file
    if check_env_file():
        print("✅ .env file exists with Ollama and Formbricks config")
    else:
        print("⚠ .env file missing or incomplete")
        print("   Copy .env.example to .env")
        print("   Make sure it has OLLAMA_URL and FORMBRICKS_API_KEY")
    
    print("\n📋 Next steps:")
    print("1. Make sure Docker Desktop is running")
    print("2. Run: python main.py formbricks up")
    print("3. Setup your Formbricks admin account at http://localhost:3000")
    print("4. Get Formbricks API key from Settings → API Keys")
    print("5. Run: python main.py formbricks generate")
    print("6. Run: python main.py formbricks seed")

if __name__ == "__main__":
    main()