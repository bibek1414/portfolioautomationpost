#!/usr/bin/env python3
import os
import subprocess
import sys
import json

def check_python_version():
    """Check if Python version is 3.7+"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)
    print("✓ Python version check passed")

def install_dependencies():
    """Install required Python packages"""
    try:
        packages = [
            "playwright",
            "pyautogui",
        ]
        
        print("Installing Python dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade"] + packages)
        print("✓ Dependencies installed successfully")
        
        # Install Playwright browsers
        print("Installing Playwright browsers...")
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        print("✓ Playwright browsers installed successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def create_config_template():
    """Create config.json template if it doesn't exist"""
    if not os.path.exists("config.json"):
        config = {
            "email": "your-admin-email@example.com",
            "password": "your-admin-password"
        }
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        print("✓ Created config.json template")
        print("IMPORTANT: Edit config.json to add your actual credentials")
    else:
        print("✓ config.json already exists")

def main():
    """Main setup function"""
    print("Setting up blog automation project...")
    
    check_python_version()
    install_dependencies()
    create_config_template()
    
    # Create screenshots directory
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
        print("✓ Created screenshots directory")
    
    print("\nSetup complete! You can now run the automation with:")
    print("python blog_automation.py")

if __name__ == "__main__":
    main()