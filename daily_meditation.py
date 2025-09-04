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
    
    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Initialize Chrome WebDriver with webdriver-manager
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service as ChromeService
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            # Navigate to Google Voice
            driver.get("https://voice.google.com")
            print("Opened Google Voice homepage")
            
            # Wait for and click sign in button
            try:
                sign_in_btn = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Sign in')]"))
                )
                sign_in_btn.click()
                print("Clicked sign in button")
            except Exception as e:
                print("Might already be on login page")
            
            # Handle email entry
            try:
                email_field = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.ID, "identifierId"))
                )
                email_field.clear()
                email_field.send_keys(gvoice_config["email"])
                print("Entered email")
                
                # Click next
                next_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "identifierNext"))
                )
                next_btn.click()
                print("Clicked next after email")
            except Exception as e:
                print(f"Email entry failed: {e}")
                raise
            
            # Handle password entry
            try:
                password_field = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.NAME, "Passwd"))
                )
                time.sleep(2)  # Small delay
                password_field.clear()
                password_field.send_keys(gvoice_config["password"])
                print("Entered password")
                
                # Click next
                next_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "passwordNext"))
                )
                next_btn.click()
                print("Clicked sign in button")
            except Exception as e:
                print(f"Password entry failed: {e}")
                raise
            
            # Wait for Google Voice to load
            print("Waiting for Google Voice to load...")
            time.sleep(15)  # Increased wait time for page to load
            
            # Verify login was successful
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Messages')]"))
                )
                print("Successfully logged in to Google Voice")
            except Exception as e:
                print("Failed to verify Google Voice login")
                # Take a screenshot for debugging
                driver.save_screenshot("login_error.png")
                print("Saved screenshot as login_error.png")
                raise
            
            # Format the message
            message = f"Daily Meditation #{meditation_number}:\n\n{meditation}"
            
            # Send SMS to each recipient
            for recipient in config["recipients"]:
                try:
                    # Clean the phone number
                    phone = re.sub(r'[^\d+]', '', recipient)
                    
                    try:
                        # Click on Messages tab
                        print(f"Attempting to send to {phone}...")
                        messages_btn = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Messages')]"))
                        )
                        messages_btn.click()
                        print("Clicked Messages tab")
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
                        
                        # Wait for message to send
                        time.sleep(5)
                        
                        # Take a screenshot for verification
                        driver.save_screenshot(f"sent_{phone}.png")
                        print(f"Saved screenshot as sent_{phone}.png")
                        
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
