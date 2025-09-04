#!/usr/bin/env python3
"""
Test script for Google Voice login and message sending.
This script helps diagnose issues with the Google Voice automation.
"""
import os
import sys
import time
import logging
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    WebDriverException
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('google_voice_test.log')
    ]
)
logger = logging.getLogger(__name__)

class GoogleVoiceTester:
    """Test Google Voice login and message sending functionality."""
    
    def __init__(self, email: str, password: str, headless: bool = False):
        """Initialize with Google Voice credentials."""
        self.email = email
        self.password = password
        self.headless = headless
        self.driver = None
        self.debug_dir = Path("debug_test")
        self.debug_dir.mkdir(exist_ok=True)
        self.screenshot_count = 0
    
    def setup_driver(self):
        """Set up the Chrome WebDriver."""
        try:
            options = Options()
            
            if self.headless:
                options.add_argument("--headless=new")
            
            # Performance and compatibility options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-software-rasterizer")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # User agent
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            options.add_argument(f'user-agent={user_agent}')
            
            # Experimental options
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Initialize Chrome WebDriver
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(10)
            
            logger.info("Chrome WebDriver initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            return False
    
    def save_screenshot(self, prefix: str = "screenshot") -> str:
        """Save a screenshot with an auto-incrementing number."""
        if not self.driver:
            return ""
            
        self.screenshot_count += 1
        filename = f"{self.screenshot_count:03d}_{prefix}.png"
        filepath = self.debug_dir / filename
        
        try:
            self.driver.save_screenshot(str(filepath))
            logger.debug(f"Saved screenshot: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
            return ""
    
    def save_page_source(self, prefix: str = "page") -> str:
        """Save the current page source."""
        if not self.driver:
            return ""
            
        filename = f"{prefix}_{int(time.time())}.html"
        filepath = self.debug_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            logger.debug(f"Saved page source: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to save page source: {e}")
            return ""
    
    def login(self) -> bool:
        """Log in to Google Voice."""
        if not self.driver:
            logger.error("WebDriver not initialized")
            return False
        
        try:
            # Navigate to Google Voice
            logger.info("Navigating to Google Voice...")
            self.driver.get("https://voice.google.com/")
            self.save_screenshot("initial_page")
            
            # Check if already logged in
            if "accounts.google.com" not in self.driver.current_url:
                logger.info("Already logged in")
                return True
            
            # Enter email
            logger.info("Entering email...")
            try:
                email_field = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "identifierId"))
                )
                email_field.clear()
                email_field.send_keys(self.email)
                self.save_screenshot("email_entered")
                
                # Click Next
                next_button = self.driver.find_element(By.ID, "identifierNext")
                next_button.click()
                logger.info("Submitted email")
                self.save_screenshot("email_submitted")
                
            except Exception as e:
                logger.error(f"Error entering email: {e}")
                self.save_screenshot("email_error")
                return False
            
            # Enter password
            logger.info("Entering password...")
            try:
                # Wait for password field to be visible
                password_field = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.NAME, "Passwd"))
                )
                
                # Sometimes there's a delay before the field is ready
                time.sleep(2)
                
                password_field.clear()
                password_field.send_keys(self.password)
                self.save_screenshot("password_entered")
                
                # Click Next
                next_button = self.driver.find_element(By.ID, "passwordNext")
                next_button.click()
                logger.info("Submitted password")
                self.save_screenshot("password_submitted")
                
                # Wait for login to complete
                try:
                    WebDriverWait(self.driver, 20).until(
                        lambda d: "voice.google.com" in d.current_url
                    )
                    logger.info("Successfully logged in")
                    self.save_screenshot("login_success")
                    return True
                    
                except TimeoutException:
                    logger.error("Login timeout - check for 2FA or security challenges")
                    self.save_screenshot("login_timeout")
                    return False
                
            except Exception as e:
                logger.error(f"Error entering password: {e}")
                self.save_screenshot("password_error")
                return False
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            self.save_screenshot("login_failed")
            return False
    
    def send_test_message(self, phone_number: str, message: str) -> bool:
        """Send a test message to the specified phone number."""
        if not self.driver:
            logger.error("WebDriver not initialized")
            return False
            
        try:
            # Navigate to messages
            logger.info("Navigating to messages...")
            self.driver.get("https://voice.google.com/messages")
            self.save_screenshot("messages_page")
            
            # Wait for page to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Messages')]"))
            )
            
            # Click New Message button
            logger.info("Clicking New Message button...")
            new_msg_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label,'New message')]"))
            )
            new_msg_button.click()
            self.save_screenshot("new_message_clicked")
            
            # Enter phone number
            logger.info(f"Entering phone number: {phone_number}")
            to_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Enter a name or phone number']"))
            )
            to_field.clear()
            to_field.send_keys(phone_number)
            self.save_screenshot("phone_entered")
            
            # Enter message
            logger.info("Entering message...")
            msg_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//div[@role='textbox']"))
            )
            msg_field.clear()
            msg_field.send_keys(message)
            self.save_screenshot("message_entered")
            
            # Click Send button
            logger.info("Sending message...")
            send_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label,'Send message')]"))
            )
            send_button.click()
            self.save_screenshot("send_clicked")
            
            # Verify message was sent
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Message sent') or contains(text(),'Sent')]"))
                )
                logger.info("Message sent successfully")
                self.save_screenshot("message_sent")
                return True
                
            except TimeoutException:
                logger.warning("Could not confirm message was sent")
                self.save_screenshot("send_confirmation_missing")
                return False
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.save_screenshot("send_message_error")
            return False
    
    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed")
            except:
                pass

def main():
    """Main function for testing Google Voice."""
    import getpass
    
    print("=== Google Voice Tester ===\n")
    
    # Get credentials
    email = input("Enter your Google email: ").strip()
    password = getpass.getpass("Enter your Google password: ").strip()
    phone = input("Enter a phone number to send test message (e.g., +1234567890): ").strip()
    
    # Initialize tester
    tester = GoogleVoiceTester(email, password, headless=False)
    
    try:
        # Set up WebDriver
        if not tester.setup_driver():
            print("\nFailed to initialize WebDriver. Check logs for details.")
            return 1
        
        # Test login
        print("\nTesting login...")
        if not tester.login():
            print("\nLogin failed. Check debug directory for screenshots.")
            return 1
        
        print("\nLogin successful!")
        
        # Test message sending
        if phone:
            print("\nTesting message sending...")
            message = "This is a test message from Google Voice Tester"
            if tester.send_test_message(phone, message):
                print(f"\nTest message sent to {phone}")
            else:
                print("\nFailed to send test message. Check debug directory for screenshots.")
        
        print("\nTest completed. Check the 'debug_test' directory for screenshots and logs.")
        return 0
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        return 130
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        return 1
    finally:
        tester.cleanup()

if __name__ == "__main__":
    sys.exit(main())
