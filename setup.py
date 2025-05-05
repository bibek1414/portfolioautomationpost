import subprocess
import json
import os
import sys

def install_dependencies():
    """Install required Python packages"""
    required_packages = [
        "playwright",
        "pyautogui",
        "google-generativeai",  # For Google AI integration
        "python-dotenv"         # For environment variable management
    ]
    
    print("Installing required packages...")
    subprocess.check_call([sys.executable,"-m", "pip", "install", "--upgrade", "pip"])
    for package in required_packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable,"-m", "pip", "install", package])
    
    print("Installing Playwright browsers...")
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])

def create_config_template():
    """Create configuration template if not exists"""
    if not os.path.exists("config.json"):
        config = {
            "email": "your-email@example.com",
            "password": "your-password",
            "google_ai": {
                "api_key": "your-google-ai-api-key"
            }
        }
        
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)
        print("Created config.json template. Please edit with your credentials.")
    else:
        print("config.json already exists.")

def create_directories():
    """Create necessary directories"""
    directories = ["screenshots", "logs"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created {directory} directory.")
        else:
            print(f"{directory} directory already exists.")

def main():
    print("Setting up Blog Automation Tool...")
    install_dependencies()
    create_config_template()
    create_directories()
    print("\nSetup complete! You can now run the blog automation tool.")
    print("Usage: python blog_automation.py [--headless]")

if __name__ == "__main__":
    main()