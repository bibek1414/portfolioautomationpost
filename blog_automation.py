from playwright.sync_api import sync_playwright
import time
import os
import random
import pyautogui
from datetime import datetime
import argparse
import json
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("blog_automation.log"),
        logging.StreamHandler()
    ]
)

def load_credentials():
    """Load credentials from a config file"""
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            return config["email"], config["password"]
    except Exception as e:
        logging.error(f"Error loading credentials: {e}")
        return None, None

def load_content_templates():
    """Load blog post templates from a file"""
    try:
        with open("content_templates.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading content templates: {e}")
        return []

def generate_post_content():
    """Generate content for a new blog post"""
    templates = load_content_templates()
    
    if not templates:
        # Default template if none are loaded
        current_date = datetime.now().strftime("%Y-%m-%d")
        return {
            "title": f"Daily Update - {current_date}",
            "excerpt": f"My thoughts and updates for {current_date}",
            "content": f"# Daily Update\n\nThis is the content for {current_date}.\n\n## Key Points\n\n- Point 1\n- Point 2\n- Point 3\n\n## Conclusion\n\nThank you for reading today's update!",
            "tags": "daily,update,blog"
        }
    
    # Choose a random template
    template = random.choice(templates)
    
    # Add current date to make it unique
    current_date = datetime.now().strftime("%Y-%m-%d")
    template["title"] = f"{template['title']} - {current_date}"
    
    return template

def create_screenshots_dir():
    """Create directory for screenshots if it doesn't exist"""
    screenshots_dir = "screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
    return screenshots_dir

def take_screenshot(page, name):
    """Take a screenshot using Playwright instead of pyautogui"""
    screenshots_dir = create_screenshots_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{screenshots_dir}/{name}_{timestamp}.png"
    
    # Use Playwright's screenshot method instead of pyautogui
    page.screenshot(path=filename)
    logging.info(f"Screenshot saved: {filename}")
    return filename

def automate_blog_post():
    """Main function to automate blog post creation"""
    email, password = load_credentials()
    
    if not email or not password:
        logging.error("Credentials not found. Please set up config.json")
        return False
    
    post_content = generate_post_content()
    
    with sync_playwright() as p:
        try:
            # Launch the browser
            browser = p.chromium.launch(headless=False)  # Set to True for production
            context = browser.new_context()
            page = context.new_page()
            
            # Navigate to the login page
            logging.info("Navigating to login page...")
            page.goto("https://www.bibekbhattarai14.com.np/admin")
            
            # Check if already logged in by looking for the blog URL
            if "blog" in page.url:
                logging.info("Already logged in, proceeding to create post")
            else:
                # Fill in login form
                logging.info("Filling login form...")
                page.fill('input[type="email"]', email)
                page.fill('input[type="password"]', password)
                
                # Take screenshot before login
                take_screenshot(page, "before_login")
                
                # Click login button
                page.click('button[type="submit"]')
                
                # Wait for navigation after login
                page.wait_for_url("**/blog")
                logging.info("Successfully logged in")
            
            # Take screenshot of blog dashboard
            take_screenshot(page, "blog_dashboard")
            
            # Click on Create New Post button - FIXED SELECTOR to match React component
            logging.info("Creating new post...")
            # Looking at your React component, the button text is "Create New Post"
            page.click('text="Create New Post"', timeout=10000)
            
            # If the above fails, try alternative selectors
            if not page.url.endswith("/new"):
                logging.info("First selector failed, trying alternative...")
                # Try using a CSS class or other attribute
                page.click('a.bg-blue-600', timeout=10000)
                
                # If that fails too, try navigating directly
                if not page.url.endswith("/new"):
                    logging.info("Navigating directly to the new post page...")
                    page.goto("https://www.bibekbhattarai14.com.np/blog/new")
            
            # Wait for the post creation form to appear - FIXED SELECTOR
            logging.info("Waiting for form to load...")
            page.wait_for_selector('#title', timeout=10000)
            
            # Fill in post details
            logging.info("Filling post details...")
            page.fill('#title', post_content["title"])
            
            if "excerpt" in post_content:
                page.fill('#excerpt', post_content["excerpt"])
            
            # Fill in content
            page.fill('#content', post_content["content"])
            
            if "tags" in post_content:
                page.fill('#tags', post_content["tags"])
            
            # Take screenshot before submission
            take_screenshot(page, "before_submission")
            
            # Click Create Post button - FIXED SELECTOR to look for the button text from your React component
            # From your React component, the button will say "Create Post" or "Update Post"
            button_selector = 'button[type="submit"]'
            page.click(button_selector)
            
            # Wait for navigation back to blog page
            page.wait_for_url("**/blog", timeout=15000)
            
            # Take screenshot of confirmation
            take_screenshot(page, "post_created")
            
            logging.info(f"Successfully created post: {post_content['title']}")
            
            # Close the browser
            browser.close()
            
            return True
            
        except Exception as e:
            logging.error(f"Error during automation: {e}")
            # Take screenshot of error state using Playwright instead of pyautogui
            if 'page' in locals():
                take_screenshot(page, "error_state")
            return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate blog post creation")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    args = parser.parse_args()
    
    success = automate_blog_post()
    
    if success:
        logging.info("Blog post automation completed successfully")
    else:
        logging.error("Blog post automation failed")