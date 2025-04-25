from flask import Flask, request, send_file
import undetected_chromedriver as uc
from PIL import Image
import io
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

app = Flask(__name__)

# Common user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48"
]

@app.route("/screenshot")
def screenshot():
    url = request.args.get("url")
    if not url or not url.startswith(("http://", "https://")):
        return "Invalid or missing URL.", 400
    
    # Enhanced browser setup
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")  # More common resolution
    options.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    
    # Additional privacy settings to avoid fingerprinting
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    options.add_argument("--disable-web-security")
    
    try:
        driver = uc.Chrome(options=options)
        
        # Set additional browser parameters
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {
            "userAgent": random.choice(USER_AGENTS),
            "platform": "Windows"
        })
        
        # Set language headers
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
            "headers": {
                "Accept-Language": "en-US,en;q=0.9"
            }
        })
        
        # Navigate to the URL with a slight delay
        driver.get(url)
        
        # Wait for page to load by looking for body
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Detect and handle Cloudflare challenge
        if "Just a moment" in driver.page_source or "security check" in driver.page_source:
            # Wait longer for the Cloudflare challenge to resolve
            time.sleep(random.uniform(5, 8))
            
            # Try to find and interact with the Cloudflare checkbox if present
            try:
                checkbox = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".checkbox")))
                actions = ActionChains(driver)
                actions.move_to_element(checkbox).click().perform()
                time.sleep(random.uniform(2, 4))
            except:
                pass
            
            # Wait for the challenge to complete
            time.sleep(random.uniform(5, 8))
        
        # Inject CSS to hide scrollbars
        driver.execute_script("""
            document.documentElement.style.overflow = 'hidden';
            document.body.style.overflow = 'hidden';
        """)
        
        # Small delay to apply CSS changes
        time.sleep(0.5)
        
        # Take screenshot after human-like interaction
        png = driver.get_screenshot_as_png()
        driver.quit()
        
        # Compress image
        img = Image.open(io.BytesIO(png))
        img = img.resize((1280, int(1280 * img.height / img.width)))
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=85)
        buf.seek(0)
        
        return send_file(buf, mimetype='image/jpeg')
    
    except Exception as e:
        print(f"Error: {e}")
        return f"Failed to take screenshot: {str(e)}", 500