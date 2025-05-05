from playwright.sync_api import sync_playwright
import time
import os
import random
import logging
from datetime import datetime
import argparse
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/blog_automation.log"),
        logging.StreamHandler()
    ]
)

def load_credentials():
    """Load credentials from environment variables or config file"""
    # First try environment variables (preferred for CI/CD)
    email = os.getenv("BLOG_EMAIL")
    password = os.getenv("BLOG_PASSWORD")
    google_api_key = os.getenv("GOOGLE_AI_API_KEY")
    
    # Fall back to config file if environment variables not set
    if not (email and password):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                email = email or config.get("email")
                password = password or config.get("password")
                google_api_key = google_api_key or config.get("google_ai", {}).get("api_key")
        except Exception as e:
            logging.error(f"Error loading credentials: {e}")
    
    return email, password, google_api_key

def load_content_templates():
    """Load blog post templates from a file"""
    try:
        with open("content_templates.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading content templates: {e}")
        return []

def generate_tech_topic():
    """Generate a current tech topic to write about"""
    tech_topics = [
        "Cloud Native Architecture",
        "DevOps Best Practices",
        "Machine Learning Ethics",
        "Kubernetes in Production",
        "Serverless Computing",
        "Python Development Tips",
        "Web3 Technology",
        "Cybersecurity Trends",
        "GitHub Copilot and AI Programming",
        "Tech Industry Humor",
        "Docker Optimization",
        "API Design Principles",
        "Frontend Framework Comparison",
        "Infrastructure as Code",
        "Database Performance Tuning",
        "Tech Career Development",
        "Open Source Contributions",
        "Mobile App Development Trends",
        "Microservices Architecture",
        "AI and ML in DevOps"
    ]
    return random.choice(tech_topics)

def generate_ai_content(api_key, template=None):
    """Generate blog content using Google Generative AI"""
    if not api_key:
        logging.warning("Google AI API key not found, using templates instead")
        return None
    
    try:
        genai.configure(api_key=api_key)
        
        # Use gemini-1.5-flash model
        model = genai.GenerativeModel('gemini-1.5-flash')
        logging.info("Using model: gemini-1.5-flash")
        
        # Choose a random tech topic if no template provided
        topic = template["title"] if template else generate_tech_topic()
        
        # Create prompt for content generation
        prompt = f"""
        Create a blog post about "{topic}". The post should:
        - Be written in a slightly humorous but professional tech voice
        - Include practical insights and examples
        - Have clear sections with markdown formatting
        - Be around 500-800 words
        - Include a title, introduction, 2-4 main sections, and conclusion
        - Be related to software development, DevOps, or modern tech trends
        
        Format the post using markdown, with a # heading for the title and ## for sections.
        Also suggest 3-6 relevant tags as a comma-separated list.
        """
        
        response = model.generate_content(prompt)
        content_text = response.text
        
        # Extract title, content and tags
        lines = content_text.split('\n')
        title = lines[0].replace('# ', '') if lines and lines[0].startswith('# ') else topic
        
        # Find tags (usually at the end)
        tags = ""
        for line in lines:
            if line.lower().startswith("tags:") or line.lower().startswith("**tags:**"):
                tags = line.split(":", 1)[1].strip()
                break
        
        # If tags not found in expected format, generate some
        if not tags:
            tags = ",".join(topic.lower().split()[:3]) + ",tech,blog"
        
        # Create excerpt from first paragraph
        excerpt = ""
        for line in lines[1:]:
            if line.strip() and not line.startswith('#'):
                excerpt = line.strip()[:150]
                if len(excerpt) >= 100:
                    break
        
        return {
            "title": title,
            "excerpt": excerpt,
            "content": content_text,
            "tags": tags
        }
        
    except Exception as e:
        logging.error(f"Error generating AI content: {e}")
        return None

def generate_post_content(api_key=None):
    """Generate content for a new blog post"""
    templates = load_content_templates()
    
    # First try AI content generation if API key available
    if api_key:
        # Randomly decide whether to use a template or pure AI-generated content
        use_template_as_guide = random.choice([True, False])
        template = random.choice(templates) if templates and use_template_as_guide else None
        
        ai_content = generate_ai_content(api_key, template)
        if ai_content:
            logging.info("Using AI-generated content")
            return ai_content
    
    # Fall back to templates if AI generation fails or no API key
    if templates:
        template = random.choice(templates)
        
        # Add current date to make it unique
        current_date = datetime.now().strftime("%Y-%m-%d")
        template["title"] = f"{template['title']} - {current_date}"
        
        logging.info("Using template content")
        return template
    
    # Default content as last resort
    current_date = datetime.now().strftime("%Y-%m-%d")
    logging.info("Using default content")
    return {
        "title": f"Tech Update - {current_date}",
        "excerpt": f"Latest thoughts on technology trends for {current_date}",
        "content": f"# Tech Update\n\nThis is the content for {current_date}.\n\n## Key Points\n\n- Technology is constantly evolving\n- DevOps practices improve efficiency\n- Automation saves time\n\n## Conclusion\n\nStay updated with the latest tech trends!",
        "tags": "tech,update,devops"
    }

def create_screenshots_dir():
    """Create directory for screenshots if it doesn't exist"""
    screenshots_dir = "screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
    return screenshots_dir

def take_screenshot(page, name):
    """Take a screenshot using Playwright"""
    screenshots_dir = create_screenshots_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{screenshots_dir}/{name}_{timestamp}.png"
    
    # Use Playwright's screenshot method
    page.screenshot(path=filename)
    logging.info(f"Screenshot saved: {filename}")
    return filename

def check_existing_post(page, title):
    """Check if a post with similar title already exists"""
    try:
        # Navigate to blog listing page if not already there
        if not page.url.endswith("/blog"):
            page.goto("https://www.bibekbhattarai14.com.np/blog")
        
        # Look for the title in the page content
        title_words = set(word.lower() for word in title.split() if len(word) > 3)
        page_content = page.content().lower()
        
        match_count = sum(1 for word in title_words if word in page_content)
        match_percentage = match_count / len(title_words) if title_words else 0
        
        if match_percentage > 0.7:  # If more than 70% of significant words match
            logging.warning(f"A similar post may already exist for: {title}")
            return True
        
        return False
        
    except Exception as e:
        logging.error(f"Error checking existing posts: {e}")
        return False  # Proceed with posting if check fails

def automate_blog_post(headless=False):
    """Main function to automate blog post creation"""
    email, password, google_api_key = load_credentials()
    
    if not email or not password:
        logging.error("Credentials not found. Please set up environment variables or config.json")
        return False
    
    post_content = generate_post_content(google_api_key)
    
    with sync_playwright() as p:
        try:
            # Launch the browser
            browser = p.chromium.launch(headless=headless)
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
                page.wait_for_url("**/blog", timeout=15000)
                logging.info("Successfully logged in")
            
            # Take screenshot of blog dashboard
            take_screenshot(page, "blog_dashboard")
            
            # Check if similar post exists
            if check_existing_post(page, post_content["title"]):
                logging.info("Modifying title to avoid duplication")
                post_content["title"] = f"{post_content['title']} (v{random.randint(2, 99)})"
            
            # Click on Create New Post button
            logging.info("Creating new post...")
            try:
                page.click('text="Create New Post"', timeout=10000)
            except:
                # Try alternative selectors if the first one fails
                try:
                    page.click('a.bg-blue-600', timeout=5000)
                except:
                    # Navigate directly as last resort
                    page.goto("https://www.bibekbhattarai14.com.np/blog/new")
            
            # Wait for the post creation form to appear
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
            
            # Click Create Post button
            button_selector = 'button[type="submit"]'
            page.click(button_selector)
            
            # Wait for navigation back to blog page
            page.wait_for_url("**/blog", timeout=15000)
            
            # Take screenshot of confirmation
            take_screenshot(page, "post_created")
            
            logging.info(f"Successfully created post: {post_content['title']}")
            
            # Save successful post details for analytics
            save_post_analytics(post_content["title"])
            
            # Close the browser
            browser.close()
            
            return True
            
        except Exception as e:
            logging.error(f"Error during automation: {e}")
            # Take screenshot of error state using Playwright
            if 'page' in locals():
                take_screenshot(page, "error_state")
            return False

def save_post_analytics(post_title):
    """Save post creation data for analytics tracking"""
    analytics_file = "post_analytics.json"
    
    try:
        # Load existing analytics data
        if os.path.exists(analytics_file):
            with open(analytics_file, "r") as f:
                analytics = json.load(f)
        else:
            analytics = {"posts": []}
        
        # Add new post data
        post_data = {
            "title": post_title,
            "created_at": datetime.now().isoformat(),
            "views": 0,  # Initial view count
            "comments": 0  # Initial comment count
        }
        
        analytics["posts"].append(post_data)
        
        # Save updated analytics data
        with open(analytics_file, "w") as f:
            json.dump(analytics, f, indent=2)
            
        logging.info(f"Analytics data saved for post: {post_title}")
        
    except Exception as e:
        logging.error(f"Error saving analytics data: {e}")

if __name__ == "__main__":
    # Create necessary directories
    if not os.path.exists("logs"):
        os.makedirs("logs")
        
    parser = argparse.ArgumentParser(description="Automate blog post creation")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    args = parser.parse_args()
    
    success = automate_blog_post(args.headless)
    
    if success:
        logging.info("Blog post automation completed successfully")
    else:
        logging.error("Blog post automation failed")