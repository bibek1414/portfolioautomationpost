import subprocess
import json
import os
import sys

def install_dependencies():
    """Install required Python packages"""
    required_packages = [
        "playwright",
        "google-generativeai",  # For Google AI integration
        "python-dotenv"         # For environment variable management
    ]
    
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    for package in required_packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("Installing Playwright browsers...")
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])

def create_config_template():
    """Create configuration template if not exists"""
    if not os.path.exists("config.json"):
        config = {
            "email": "",
            "password": "",
            "google_ai": {
                "api_key": ""
            },
            "settings": {
                "headless": True,
                "post_frequency": "daily"
            }
        }
        
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)
        print("Created config.json template. Please edit with your credentials.")
        print("NOTE: For security, consider using environment variables instead!")
    else:
        print("config.json already exists.")

def create_env_file():
    """Create .env file template if not exists"""
    if not os.path.exists(".env"):
        env_content = """# Blog credentials
BLOG_EMAIL=
BLOG_PASSWORD=

# Google AI API Key
GOOGLE_AI_API_KEY=
"""
        with open(".env", "w") as f:
            f.write(env_content)
        print("Created .env template. Please edit with your credentials.")
        print("NOTE: This file should be added to .gitignore for security!")
    else:
        print(".env file already exists.")

def create_directories():
    """Create necessary directories"""
    directories = ["screenshots", "logs"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created {directory} directory.")
        else:
            print(f"{directory} directory already exists.")

def create_gitignore():
    """Create or update .gitignore file with sensitive files"""
    gitignore_entries = [
        ".env",
        "config.json",
        "*.log",
        "__pycache__/",
        "*.py[cod]",
        "screenshots/",
        "logs/"
    ]
    
    # Read existing .gitignore if it exists
    existing_entries = set()
    if os.path.exists(".gitignore"):
        with open(".gitignore", "r") as f:
            existing_entries = set(line.strip() for line in f.readlines())
    
    # Add new entries
    with open(".gitignore", "a") as f:
        for entry in gitignore_entries:
            if entry not in existing_entries:
                f.write(f"{entry}\n")
    
    print("Updated .gitignore with sensitive files and directories.")

def create_content_template():
    """Create sample content template file"""
    if not os.path.exists("content_templates.json"):
        templates = [
            {
                "title": "Best DevOps Practices",
                "excerpt": "Exploring the most effective DevOps practices for modern development teams.",
                "content": "# Best DevOps Practices\n\nIn today's fast-paced development world, DevOps practices have become essential for delivering high-quality software efficiently.\n\n## Continuous Integration\n\nImplementing CI ensures that code changes are automatically tested and integrated into the main codebase.\n\n## Infrastructure as Code\n\nManaging infrastructure through code allows for consistent, repeatable deployments and easier scaling.\n\n## Conclusion\n\nAdopting these DevOps practices can significantly improve your team's productivity and software quality.",
                "tags": "devops,ci/cd,automation,best-practices"
            },
            {
                "title": "Python Development Tips",
                "excerpt": "Useful tips and tricks for Python developers to write cleaner, more efficient code.",
                "content": "# Python Development Tips\n\nPython's simplicity makes it accessible, but there are many advanced techniques that can enhance your code.\n\n## Use List Comprehensions\n\nList comprehensions provide a concise way to create lists based on existing lists:\n\n```python\nsquares = [x**2 for x in range(10)]\n```\n\n## Leverage Virtual Environments\n\nAlways use virtual environments to manage dependencies for different projects.\n\n## Conclusion\n\nThese practices will help you write more Pythonic, maintainable code.",
                "tags": "python,development,tips,coding"
            }
        ]
        
        with open("content_templates.json", "w") as f:
            json.dump(templates, f, indent=2)
        print("Created sample content_templates.json")
    else:
        print("content_templates.json already exists.")

def main():
    print("Setting up Blog Automation Tool...")
    install_dependencies()
    create_config_template()
    create_env_file()
    create_directories()
    create_gitignore()
    create_content_template()
    
    print("\nSetup complete! You can now run the blog automation tool.")
    print("IMPORTANT SECURITY NOTES:")
    print("1. Add your credentials to .env instead of config.json")
    print("2. Ensure .gitignore is properly configured to avoid committing credentials")
    print("3. For GitHub Actions, set up secrets in your repository settings")
    
    print("\nUsage: python blog_automation.py [--headless]")

if __name__ == "__main__":
    main()