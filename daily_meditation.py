#!/usr/bin/env python3
import random
import os
import json
import time
import re
from pathlib import Path
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration file path
CONFIG_FILE = Path(__file__).parent / "config.json"

# Daily meditations - a collection of fitness, yoga, and philosophical quotes
MEDITATIONS = [
    # Fitness quotes
    "Exercise is king. Nutrition is queen. Put them together and you've got a kingdom. — Jack LaLanne",
    "Take care of your body. It's the only place you have to live. — Jim Rohn",
    "The last three or four reps is what makes the muscle grow. This area of pain divides a champion from someone who is not a champion. — Arnold Schwarzenegger",
    "If it doesn't challenge you, it doesn't change you. — Fred DeVito",
    "The only bad workout is the one that didn't happen. — Unknown",
    "Motivation is what gets you started. Habit is what keeps you going. — Jim Ryun",
    "A year from now you may wish you had started today. — Karen Lamb",
    "Your body can stand almost anything. It's your mind that you have to convince. — Unknown",
    "Fitness is not about being better than someone else. It's about being better than you used to be. — Unknown",
    "Strength does not come from physical capacity. It comes from an indomitable will. — Mahatma Gandhi",
    "Don't count the days, make the days count. — Muhammad Ali",
    "When you feel like quitting, think about why you started. — Unknown",
    "Success usually comes to those who are too busy to be looking for it. — Henry David Thoreau",
    "The pain you feel today will be the strength you feel tomorrow. — Unknown",
    "Energy and persistence conquer all things. — Benjamin Franklin",
    
    # Yoga quotes
    "Yoga is the journey of the self, through the self, to the self. — Bhagavad Gita",
    "Yoga is not about touching your toes. It's about what you learn on the way down. — Jigar Gor",
    "The body benefits from movement, and the mind benefits from stillness. — Sakyong Mipham",
    "Yoga teaches us to cure what need not be endured and endure what cannot be cured. — B.K.S. Iyengar",
    "Calming the mind is yoga. Not just standing on the head. — Swami Satchidananda",
    "Yoga is the fountain of youth. You're only as young as your spine is flexible. — Bob Harper",
    "Yoga does not just change the way we see things, it transforms the person who sees. — B.K.S. Iyengar",
    "Yoga is a light, which once lit will never dim. The better your practice, the brighter your flame. — B.K.S. Iyengar",
    "Yoga is invigoration in relaxation. Freedom in routine. Confidence through self-control. — Terri Guillemets",
    "Yoga is the perfect opportunity to be curious about who you are. — Jason Crandell",
    "Yoga begins right where I am — not where I was yesterday or where I long to be. — Linda Sparrowe",
    "Yoga is the dance of every cell with the music of every breath that creates inner serenity and harmony. — Debasish Mridha",
    "Yoga is essentially a practice for your soul, working through the medium of your body. — Tara Fraser",
    "Yoga means addition — addition of energy, strength, and beauty to body, mind, and soul. — Amit Ray",
    "Inhale the future, exhale the past. — Unknown",
    
    # Alan Watts quotes
    "You are an aperture through which the universe is looking at and exploring itself. — Alan Watts",
    "The only way to make sense out of change is to plunge into it, move with it, and join the dance. — Alan Watts",
    "Trying to define yourself is like trying to bite your own teeth. — Alan Watts",
    "Muddy water is best cleared by leaving it alone. — Alan Watts",
    "Man suffers only because he takes seriously what the gods made for fun. — Alan Watts",
    "You didn't come into this world. You came out of it, like a wave from the ocean. — Alan Watts",
    "We do not 'come into' this world; we come out of it, as leaves from a tree. — Alan Watts",
    "To have faith is to trust yourself to the water. When you swim you don't grab hold of the water, because if you do you will sink and drown. — Alan Watts",
    "The more a thing tends to be permanent, the more it tends to be lifeless. — Alan Watts",
    "No valid plans for the future can be made by those who have no capacity for living now. — Alan Watts",
    "You are the universe experiencing itself. — Alan Watts",
    "Problems that remain persistently insoluble should always be suspected as questions asked the wrong way. — Alan Watts",
    "The meaning of life is just to be alive. It is so plain and so obvious and so simple. And yet, everybody rushes around in a great panic as if it were necessary to achieve something beyond themselves. — Alan Watts",
    "You are a function of what the whole universe is doing in the same way that a wave is a function of what the whole ocean is doing. — Alan Watts",
    "The ego is nothing other than the focus of conscious attention. — Alan Watts",
    "The more you try to control something, the more it controls you. — Alan Watts",
    "No amount of self-improvement can save you from being who you are. — Alan Watts",
    "Waking up to who you are requires letting go of who you imagine yourself to be. — Alan Watts",
    "Things are as they are. Looking out into the universe at night, we make no comparisons between right and wrong stars, nor between well and badly arranged constellations. — Alan Watts",
    "We cannot be more sensitive to pleasure without being more sensitive to pain. — Alan Watts",
    "You are under no obligation to be the same person you were five minutes ago. — Alan Watts",
    "No one is more dangerously insane than one who is sane all the time: he is like a steel bridge without flexibility. — Alan Watts",
    "The art of living… is neither careless drifting on the one hand nor fearful clinging to the past on the other. It consists in being sensitive to each moment, in regarding it as utterly new and unique, in having the mind open and wholly receptive. — Alan Watts",
    "Life exists only at this very moment, and in this moment it is infinite and eternal. — Alan Watts",
    "The meaning of life is just to be alive. — Alan Watts",
    "You are an intimate part of the universe; you are not just in it, you are it. — Alan Watts",
    "The mind always fails first, not the body. The secret is to make the mind work for you, not against you. — Alan Watts",
    "Every step you take is a journey through the universe. — Alan Watts",
    "Muddy water, let it settle, and the way will appear. — Alan Watts"
]

def load_config():
    """Load configuration from config file."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Default configuration
        return {
            "gvoice": {
                "email": "your-email@gmail.com",
                "password": "your-google-password",
                "phone_number": "your-google-voice-number"
            },
            "recipients": ["+1234567890"],  # List of phone numbers with country code
            "history_size": 7,
            "history": []
        }

def save_config(config):
    """Save configuration to config file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def select_random_meditation(config):
    """Select a random meditation that hasn't been sent recently."""
    history = set(config.get("history", []))
    available_meditations = [m for m in range(len(MEDITATIONS)) if m not in history]
    
    if not available_meditations:
        # If we've used all meditations, reset history
        available_meditations = list(range(len(MEDITATIONS)))
        history = set()
    
    selected = random.choice(available_meditations)
    
    # Update history
    history.add(selected)
    if len(history) > config.get("history_size", 7):
        history.remove(next(iter(history)))  # Remove oldest entry
    
    config["history"] = list(history)
    save_config(config)
    
    return MEDITATIONS[selected], selected + 1

def send_sms(config, meditation, meditation_number):
    """Send an SMS with the daily meditation to all recipients using Google Voice via Selenium."""
    gvoice_config = config["gvoice"]
    
    # Create debug directory
    debug_dir = Path("debug_logs")
    debug_dir.mkdir(exist_ok=True)
    
    def save_debug_info(prefix):
        """Save debug information including page source and screenshot."""
        timestamp = int(time.time())
        try:
            # Save page source
            with open(debug_dir / f"{prefix}_{timestamp}.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            # Save screenshot
            driver.save_screenshot(str(debug_dir / f"{prefix}_{timestamp}.png"))
            print(f"Saved debug info: {prefix}_{timestamp}")
        except Exception as e:
            print(f"Error saving debug info: {e}")
    
    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  # New headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Set user agent to look more like a regular browser
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        chrome_options.add_argument(f'user-agent={user_agent}')
        
        # Initialize Chrome WebDriver with webdriver-manager
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service as ChromeService
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            # Navigate to Google Voice with clean state
            print("Navigating to Google Voice...")
            driver.delete_all_cookies()
            
            # Try direct login URL first
            login_url = "https://accounts.google.com/ServiceLogin?service=grandcentral&continue=https://voice.google.com/u/0/messages"
            driver.get(login_url)
            print(f"Opened URL: {driver.current_url}")
            
            # Save initial state
            driver.save_screenshot("00_initial_page.png")
            print("Saved initial screenshot")
            
            # Check if we need to sign in
            if not any(x in driver.current_url for x in ["accounts.google.com", "signin", "login"]):
                # Try direct access to Google Voice
                driver.get("https://voice.google.com/messages")
                print("Attempting direct access to Google Voice")
            
            # Save login page state
            with open("01_login_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("Saved login page source")
            
            # Handle email entry with retries and better error handling
            print("Starting email entry process...")
            email_entered = False
            
            for attempt in range(1, 4):  # Try up to 3 times
                try:
                    print(f"Attempt {attempt}: Looking for email field...")
                    email_selectors = [
                        (By.ID, "identifierId"),
                        (By.NAME, "identifier"),
                        (By.CSS_SELECTOR, "input[type='email']"),
                        (By.XPATH, "//input[@type='email']")
                    ]
                    
                    email_field = None
                    for selector in email_selectors:
                        try:
                            email_field = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located(selector)
                            )
                            print(f"Found email field using {selector}")
                            break
                        except Exception as e:
                            print(f"Email field not found with {selector}: {str(e)}")
                    
                    if not email_field:
                        # Check if already logged in
                        if "voice.google.com" in driver.current_url:
                            print("Already logged in, proceeding to messages")
                            return
                        raise Exception("Could not find email field with any selector")
                    
                    # Clear and enter email
                    print("Entering email...")
                    email_field.clear()
                    time.sleep(0.5)
                    
                    # Type email character by character to mimic human typing
                    for char in gvoice_config["email"]:
                        email_field.send_keys(char)
                        time.sleep(0.05)
                    
                    print("Email entered")
                    
                    # Find and click next button with multiple selectors and retries
                    next_btn = None
                    next_btn_selectors = [
                        (By.ID, "identifierNext"),
                        (By.XPATH, "//button[.//span[text()='Next'] or @id='next']"),
                        (By.XPATH, "//span[text()='Next']/ancestor::button"),
                        (By.CSS_SELECTOR, "button[type='button']")
                    ]
                    
                    for selector in next_btn_selectors:
                        try:
                            next_btn = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable(selector)
                            )
                            print(f"Found next button using {selector}")
                            break
                        except:
                            continue
                    
                    if not next_btn:
                        raise Exception("Could not find next button with any selector")
                    
                    # Scroll into view and click using JavaScript
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                    time.sleep(0.5)
                    
                    # Try multiple click methods
                    try:
                        next_btn.click()
                    except:
                        driver.execute_script("arguments[0].click();", next_btn)
                    
                    print("Clicked next after email")
                    email_entered = True
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    print(f"Attempt {attempt} failed: {str(e)}")
                    if attempt == 3:  # Last attempt
                        driver.save_screenshot("email_entry_failed.png")
                        with open("email_entry_failed.html", "w", encoding="utf-8") as f:
                            f.write(driver.page_source)
                        raise
                    print("Retrying email entry...")
                    time.sleep(2)  # Wait before retry
            
            if not email_entered:
                raise Exception("Failed to enter email after multiple attempts")
                
            # Wait for password field with retries and better error handling
            print("Waiting for password field...")
            password_entered = False
            
            for attempt in range(1, 4):  # Try up to 3 times
                try:
                    # Save current state for debugging
                    driver.save_screenshot(f"02_before_password_attempt_{attempt}.png")
                    with open(f"02_password_page_source_{attempt}.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    print(f"Saved password page state (attempt {attempt})")
                    
                    # Check for 2FA challenge or suspicious activity
                    if any(x in driver.current_url for x in ["challenge", "verification"]):
                        raise Exception("2FA challenge detected. Please check your Google account settings to allow less secure apps or disable 2FA for this automation.")
                    
                    # Try multiple password field selectors
                    password_field = None
                    password_selectors = [
                        (By.NAME, "Passwd"),
                        (By.NAME, "password"),
                        (By.XPATH, "//input[@type='password']"),
                        (By.CSS_SELECTOR, "input[type='password']"),
                        (By.XPATH, "//input[@name='password' or @name='Passwd']")
                    ]
                    
                    for selector in password_selectors:
                        try:
                            password_field = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located(selector)
                            )
                            print(f"Found password field using {selector}")
                            break
                        except Exception as e:
                            print(f"Password field not found with {selector}: {str(e)}")
                    
                    if not password_field:
                        # Check if we're already on Google Voice
                        if "voice.google.com" in driver.current_url:
                            print("Already on Google Voice, proceeding...")
                            return
                        raise Exception("Could not find password field with any selector")
                    
                    # Clear and enter password with delay
                    print("Entering password...")
                    password_field.clear()
                    time.sleep(0.5)
                    
                    # Type password character by character with random delays
                    for char in gvoice_config["password"]:
                        password_field.send_keys(char)
                        time.sleep(random.uniform(0.05, 0.15))  # Random delay between keypresses
                    
                    print("Password entered")
                    
                    # Find and click sign in button
                    sign_in_btn = None
                    sign_in_btn_selectors = [
                        (By.ID, "passwordNext"),
                        (By.XPATH, "//button[.//span[text()='Next' or text()='Sign in']]"),
                        (By.CSS_SELECTOR, "button[type='button']"),
                        (By.XPATH, "//span[contains(text(),'Next') or contains(text(),'Sign in')]/ancestor::button")
                    ]
                    
                    for selector in sign_in_btn_selectors:
                        try:
                            sign_in_btn = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable(selector)
                            )
                            print(f"Found sign in button using {selector}")
                            break
                        except:
                            continue
                    
                    if not sign_in_btn:
                        raise Exception("Could not find sign in button with any selector")
                    
                    # Scroll into view and highlight the button
                    driver.execute_script("""
                        arguments[0].scrollIntoView({block: 'center'});
                        arguments[0].style.border = '2px solid red';
                        arguments[0].style.boxShadow = '0 0 10px red';
                    """, sign_in_btn)
                    time.sleep(0.5)
                    
                    # Try multiple click methods
                    try:
                        sign_in_btn.click()
                        print("Clicked sign in button using direct click")
                    except:
                        try:
                            driver.execute_script("arguments[0].click();", sign_in_btn)
                            print("Clicked sign in button using JavaScript")
                        except Exception as e:
                            print(f"JavaScript click failed: {str(e)}")
                            from selenium.webdriver.common.keys import Keys
                            sign_in_btn.send_keys(Keys.RETURN)
                            print("Sent ENTER key to sign in button")
                    
                    # Wait for navigation or login to complete
                    WebDriverWait(driver, 15).until(
                        lambda d: "voice.google.com" in d.current_url or 
                                "challenge" in d.current_url or
                                any(x in d.page_source.lower() for x in ["welcome", "inbox", "messages"])
                    )
                    
                    print("Successfully completed sign in")
                    password_entered = True
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    print(f"Password entry attempt {attempt} failed: {str(e)}")
                    if attempt == 3:  # Last attempt
                        driver.save_screenshot("password_entry_failed.png")
                        with open("password_entry_failed.html", "w", encoding="utf-8") as f:
                            f.write(driver.page_source)
                        raise
                    print("Retrying password entry...")
                    time.sleep(2)  # Wait before retry
            
            if not password_entered:
                raise Exception("Failed to complete password entry after multiple attempts")
                
            # Final verification of successful login
            try:
                WebDriverWait(driver, 20).until(
                    lambda d: "voice.google.com" in d.current_url
                )
                print("Successfully logged in to Google Voice")
                driver.save_screenshot("login_success.png")
                
            except Exception as e:
                print(f"Warning: May not have reached Google Voice: {str(e)}")
                driver.save_screenshot("login_verification_failed.png")
                # Continue anyway, as we might still be able to proceed
                print("Proceeding with Google Voice access...")
                
            # Now we should be on the Google Voice messages page
            print("Verifying Google Voice messages page...")
            try:
                # Wait for the messages container to be visible
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label, 'Messages')]"))
                )
                print("Successfully loaded Google Voice messages page")
                driver.save_screenshot("google_voice_ready.png")
                
            except Exception as e:
                print(f"Warning: Could not verify Google Voice messages page: {str(e)}")
                driver.save_screenshot("google_voice_verification_failed.png")
                # Continue anyway, as we might still be able to send messages
                print("Attempting to proceed with message sending...")
            
            # Try to detect if we're on a Google sign-in page
            if "accounts.google.com" in driver.current_url or any(
                x in driver.page_source.lower() 
                for x in ["sign in", "signin", "log in", "login"]
            ):
                print("Detected Google sign-in page")
                # Save page source for debugging
                with open("page_source.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print("Saved page source to page_source.html")
            else:
                try:
                    print("Looking for sign in button...")
                    # Try multiple possible sign-in button selectors
                    sign_in_selectors = [
                        (By.XPATH, "//a[contains(., 'Sign in') or contains(., 'Sign in to Google')]"),
                        (By.XPATH, "//button[contains(., 'Sign in')]"),
                        (By.XPATH, "//span[contains(., 'Sign in')]/ancestor::button"),
                        (By.XPATH, "//div[contains(@aria-label, 'Sign in')]")
                    ]
                    
                    sign_in_btn = None
                    for selector in sign_in_selectors:
                        try:
                            sign_in_btn = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable(selector)
                            )
                            print(f"Found sign in button with selector: {selector}")
                            break
                        except:
                            continue
                    
                    if not sign_in_btn:
                        raise Exception("Could not find sign in button with any selector")
                    
                    # Scroll into view and click using JavaScript
                    driver.execute_script("arguments[0].scrollIntoView(true);", sign_in_btn)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", sign_in_btn)
                    print("Clicked sign in button")
                    
                    # Wait for the login page to load
                    WebDriverWait(driver, 20).until(
                        lambda d: "accounts.google.com" in d.current_url or 
                                any(x in d.page_source.lower() for x in ["sign in", "signin", "log in", "login"])
                    )
                    print("Navigated to login page")
                    
                except Exception as e:
                    print(f"Error during sign in: {str(e)}")
                    driver.save_screenshot("sign_in_error.png")
                    with open("page_source.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    print("Saved screenshot: sign_in_error.png")
                    print("Saved page source to page_source.html")
                    raise
                    print("Clicked sign in button")
                    
                    # Wait for login page to load
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.ID, "identifierId"))
                    )
                    print("Login page loaded")
                except Exception as e:
                    print(f"Error during sign in: {str(e)}")
                    driver.save_screenshot("sign_in_error.png")
                    print("Saved screenshot: sign_in_error.png")
                    raise
            
            # Handle email entry
            try:
                print("Waiting for email field...")
                email_field = WebDriverWait(driver, 30).until(
                    EC.visibility_of_element_located((By.ID, "identifierId"))
                )
                print("Email field found, entering email...")
                email_field.clear()
                time.sleep(1)  # Small delay
                email_field.send_keys(gvoice_config["email"])
                print("Email entered")
                
                # Save screenshot before clicking next
                driver.save_screenshot("before_email_next.png")
                
                # Click next
                print("Looking for next button...")
                next_btn = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.ID, "identifierNext"))
                )
                # Scroll into view and click using JavaScript
                driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", next_btn)
                print("Clicked next after email")
                
                # Wait for password field to appear
                time.sleep(2)  # Wait for any animations
                driver.save_screenshot("after_email_next.png")
                
            except Exception as e:
                print(f"Email entry failed: {str(e)}")
                driver.save_screenshot("email_entry_error.png")
                print("Saved screenshot: email_entry_error.png")
                raise
            
            # Handle password entry
            try:
                print("Waiting for password field...")
                # Save current page source for debugging
                with open("password_page_source.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print("Saved password page source")
                
                # Try multiple possible password field selectors
                password_selectors = [
                    (By.NAME, "Passwd"),
                    (By.NAME, "password"),
                    (By.XPATH, "//input[@type='password']"),
                    (By.CSS_SELECTOR, "input[type='password']"),
                    (By.XPATH, "//input[@name='password' or @name='Passwd']"),
                    (By.CSS_SELECTOR, "input[name='password'], input[name='Passwd']")
                ]
                
                password_field = None
                for selector in password_selectors:
                    try:
                        password_field = WebDriverWait(driver, 15).until(
                            EC.visibility_of_element_located(selector)
                        )
                        print(f"Found password field using {selector}")
                        break
                    except Exception as e:
                        print(f"Tried selector {selector}, but got: {str(e)}")
                        continue
                
                if not password_field:
                    # Take screenshot and save page source for debugging
                    driver.save_screenshot("password_field_not_found.png")
                    with open("password_page_source.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    raise Exception("Could not find password field with any selector")
                
                print("Password field found, entering password...")
                # Clear and enter password with delay
                password_field.clear()
                time.sleep(1)
                
                # Type password character by character
                for char in gvoice_config["password"]:
                    password_field.send_keys(char)
                    time.sleep(0.1)  # Small delay between keypresses
                
                print("Password entered")
                
                # Save screenshot before clicking sign in
                driver.save_screenshot("before_sign_in.png")
                
                # Find and click sign in button with multiple selectors
                print("Looking for sign in button...")
                sign_in_btn_selectors = [
                    (By.ID, "passwordNext"),
                    (By.XPATH, "//button[.//span[text()='Next' or text()='Sign in']]"),
                    (By.CSS_SELECTOR, "button[type='button'] span:contains('Next'), button[type='button'] span:contains('Sign in')"),
                    (By.XPATH, "//span[contains(text(),'Next') or contains(text(),'Sign in')]/ancestor::button"),
                    (By.CSS_SELECTOR, "button[data-idom-class*='signin']")
                ]
                
                sign_in_btn = None
                for selector in sign_in_btn_selectors:
                    try:
                        sign_in_btn = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable(selector)
                        )
                        print(f"Found sign in button using {selector}")
                        break
                    except Exception as e:
                        print(f"Tried sign in button selector {selector}, but got: {str(e)}")
                        continue
                
                if not sign_in_btn:
                    raise Exception("Could not find sign in button with any selector")
                
                # Scroll into view and click using JavaScript
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sign_in_btn)
                time.sleep(1)
                
                # Try multiple ways to click the button
                try:
                    # First try direct click
                    sign_in_btn.click()
                except:
                    try:
                        # Try with JavaScript click
                        driver.execute_script("arguments[0].click();", sign_in_btn)
                    except Exception as e:
                        print(f"JavaScript click failed: {str(e)}")
                        # As last resort, try sending ENTER key
                        from selenium.webdriver.common.keys import Keys
                        sign_in_btn.send_keys(Keys.RETURN)
                
                print("Clicked sign in button")
                
                # Wait for Google Voice to load with more robust waiting
                print("Waiting for sign in to complete...")
                try:
                    # Wait for either Google Voice to load or for 2FA if needed
                    WebDriverWait(driver, 30).until(
                        lambda d: "voice.google.com" in d.current_url or 
                                "challenge/selection" in d.current_url or
                                "challenge/2" in d.current_url
                    )
                    print("Successfully signed in")
                except Exception as e:
                    print(f"Warning: May not have completed sign in: {str(e)}")
                
                # Save final state
                time.sleep(3)  # Wait for any final redirects
                driver.save_screenshot("after_sign_in.png")
                
            except Exception as e:
                print(f"Password entry failed: {str(e)}")
                driver.save_screenshot("password_entry_error.png")
                print("Saved screenshot: password_entry_error.png")
                raise
            
            # Wait for Google Voice to load with more robust verification
            print("Waiting for Google Voice to load...")
            
            # Save current state for debugging
            driver.save_screenshot("before_voice_verification.png")
            with open("voice_page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("Saved initial voice page state")
            
            # Check for 2FA challenge
            if "challenge/selection" in driver.current_url or "challenge/2" in driver.current_url:
                print("2FA challenge detected. Manual intervention required.")
                driver.save_screenshot("2fa_challenge.png")
                raise Exception("2FA authentication required. Please check the Google account settings to allow less secure apps or disable 2FA for this automation.")
            
            # Wait for Google Voice to be fully loaded
            try:
                # Try multiple indicators that the page has loaded
                WebDriverWait(driver, 30).until(
                    lambda d: any([
                        d.execute_script("return document.readyState === 'complete'"),
                        d.find_elements(By.XPATH, "//div[contains(text(),'Messages')]"),
                        d.find_elements(By.XPATH, "//div[contains(@aria-label, 'Messages')]"),
                        d.find_elements(By.XPATH, "//*[contains(text(),'Messages')]"),
                        d.find_elements(By.XPATH, "//*[contains(@aria-label, 'Messages')]")
                    ])
                )
                print("Google Voice page loaded successfully")
                
                # Additional verification that we're actually logged in
                if "accounts.google.com" in driver.current_url:
                    raise Exception("Still on login page after successful login attempt")
                    
                # Check for any error messages
                error_messages = driver.find_elements(By.XPATH, "//*[contains(text(),'error') or contains(text(),'Error') or contains(text(),'try again')]")
                if error_messages:
                    error_text = " | ".join([e.text for e in error_messages if e.text.strip()])
                    print(f"Warning: Possible error messages found: {error_text}")
                    driver.save_screenshot("warning_messages.png")
                
                # Save final state
                driver.save_screenshot("voice_loaded.png")
                
            except Exception as e:
                print(f"Failed to verify Google Voice login: {str(e)}")
                # Take screenshots for debugging
                driver.save_screenshot("login_verification_error.png")
                with open("login_page_source.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print("Saved error screenshots and page source")
                
                # Check if we're on a "suspicious sign-in" page
                if "suspicious" in driver.page_source.lower() or "suspicious" in driver.current_url:
                    raise Exception("Suspicious sign-in detected. Please check your Google account for security alerts.")
                
                # Check for rate limiting
                if "try again later" in driver.page_source.lower() or "too many attempts" in driver.page_source.lower():
                    raise Exception("Rate limited by Google. Please try again later.")
                
                # If we got this far but still have an issue, raise the original error
                raise
            
            # Format the message
            message = f"Daily Meditation #{meditation_number}:\n\n{meditation}"
            print(f"Prepared message: {message[:50]}...")
            
            # Save current state before sending
            save_debug_info("before_sending")
            
            # Send SMS to each recipient
            for recipient in config["recipients"]:
                try:
                    print(f"\n=== Processing recipient: {recipient} ===")
                    # Clean the phone number
                    phone = re.sub(r'[^\d+]', '', recipient)
                    
                    try:
                        # Click on Messages tab
                        print(f"Attempting to send to {phone}...")
                        save_debug_info(f"before_messages_click_{phone}")
                        
                        # Try multiple selectors for Messages tab
                        messages_selectors = [
                            (By.XPATH, "//div[contains(text(),'Messages')]"),
                            (By.XPATH, "//span[contains(text(),'Messages')]"),
                            (By.XPATH, "//*[contains(@aria-label, 'Messages')]")
                        ]
                        
                        messages_btn = None
                        for selector in messages_selectors:
                            try:
                                messages_btn = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable(selector)
                                )
                                print(f"Found Messages tab with selector: {selector}")
                                break
                            except Exception as e:
                                print(f"Messages tab not found with {selector}: {e}")
                        
                        if not messages_btn:
                            raise Exception("Could not find Messages tab with any selector")
                            
                        # Scroll into view and click
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", messages_btn)
                        time.sleep(1)
                        messages_btn.click()
                        print("Clicked Messages tab")
                        save_debug_info(f"after_messages_click_{phone}")
                        time.sleep(2)
                        
                        # Click on New Message
                        new_msg_btn = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label,'New message')]"))
                        )
                        new_msg_btn.click()
                        print("Clicked New Message button")
                        time.sleep(2)
                        
                        # Enter phone number
                        to_field = WebDriverWait(driver, 20).until(
                            EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Enter a name or phone number']"))
                        )
                        to_field.clear()
                        to_field.send_keys(phone)
                        print(f"Entered phone number: {phone}")
                        time.sleep(1)
                        
                        # Enter message
                        msg_field = WebDriverWait(driver, 20).until(
                            EC.visibility_of_element_located((By.XPATH, "//div[@role='textbox']"))
                        )
                        msg_field.clear()
                        msg_field.send_keys(message)
                        print("Entered message")
                        time.sleep(1)
                        
                        # Click send
                        send_btn = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label,'Send message')]"))
                        )
                        send_btn.click()
                        print(f"Successfully sent SMS to {phone}")
                        
                        # Wait for message to send with verification
                        print("Waiting for message to send...")
                        sent = False
                        for _ in range(10):  # Wait up to 10 seconds
                            if "Message sent" in driver.page_source or "Sent" in driver.page_source:
                                sent = True
                                break
                            time.sleep(1)
                        
                        if sent:
                            print(f"✅ Successfully sent SMS to {phone}")
                        else:
                            print(f"⚠️ Message may not have been sent to {phone}")
                        
                        # Save debug info
                        save_debug_info(f"after_send_{phone}")
                        time.sleep(2)  # Small delay between recipients
                        
                    except Exception as e:
                        print(f"Error in sending process: {e}")
                        # Take a screenshot on error
                        driver.save_screenshot(f"error_{phone}.png")
                        print(f"Saved error screenshot as error_{phone}.png")
                        raise
                    
                except Exception as e:
                    print(f"Failed to send SMS to {recipient}: {str(e)}")
                    continue
                    
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        raise

def main():
    """Main function to send daily meditation via SMS."""
    try:
        # Load configuration
        config = load_config()
        
        # Select a random meditation
        meditation, meditation_number = select_random_meditation(config)
        
        # Send SMS
        send_sms(config, meditation, meditation_number)
        print(f"Successfully sent meditation #{meditation_number} via SMS")
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
