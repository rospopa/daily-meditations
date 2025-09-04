#!/usr/bin/env python3
import random
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import os
import json
from pathlib import Path
import sys

# Configuration file path
CONFIG_FILE = Path(__file__).parent / "config.json"

# Proverbs from Proverbs 22:17-24:22 - The Sayings of the Wise
PROVERBS = [
    "Pay attention and turn your ear to the sayings of the wise; apply your heart to what I teach, for it is pleasing when you keep them in your heart and have all of them ready on your lips. (Proverbs 22:17-18)",
    "So that your trust may be in the LORD, I teach you today, even you. (Proverbs 22:19)",
    "Have I not written thirty sayings for you, sayings of counsel and knowledge, teaching you to be honest and to speak the truth, so that you bring back truthful reports to those you serve? (Proverbs 22:20-21)",
    "Do not exploit the poor because they are poor and do not crush the needy in court, for the LORD will take up their case and will exact life for life. (Proverbs 22:22-23)",
    "Do not make friends with a hot-tempered person, do not associate with one easily angered, or you may learn their ways and get yourself ensnared. (Proverbs 22:24-25)",
    "Do not be one who shakes hands in pledge or puts up security for debts; if you lack the means to pay, your very bed will be snatched from under you. (Proverbs 22:26-27)",
    "Do not move an ancient boundary stone set up by your ancestors. (Proverbs 22:28)",
    "Do you see someone skilled in their work? They will serve before kings; they will not serve before officials of low rank. (Proverbs 22:29)",
    "When you sit to dine with a ruler, note well what is before you, and put a knife to your throat if you are given to gluttony. Do not crave his delicacies, for that food is deceptive. (Proverbs 23:1-3)",
    "Do not wear yourself out to get rich; do not trust your own cleverness. Cast but a glance at riches, and they are gone, for they will surely sprout wings and fly off to the sky like an eagle. (Proverbs 23:4-5)",
    "Do not eat the food of a begrudging host, do not crave his delicacies; for he is the kind of person who is always thinking about the cost. 'Eat and drink,' he says to you, but his heart is not with you. (Proverbs 23:6-7)",
    "You will vomit up the little you have eaten and will have wasted your compliments. (Proverbs 23:8)",
    "Do not speak to fools, for they will scorn your prudent words. (Proverbs 23:9)",
    "Do not move an ancient boundary stone or encroach on the fields of the fatherless, for their Defender is strong; he will take up their case against you. (Proverbs 23:10-11)",
    "Apply your heart to instruction and your ears to words of knowledge. (Proverbs 23:12)",
    "Do not withhold discipline from a child; if you punish them with the rod, they will not die. Punish them with the rod and save them from death. (Proverbs 23:13-14)",
    "My son, if your heart is wise, then my heart will be glad indeed; my inmost being will rejoice when your lips speak what is right. (Proverbs 23:15-16)",
    "Do not let your heart envy sinners, but always be zealous for the fear of the LORD. There is surely a future hope for you, and your hope will not be cut off. (Proverbs 23:17-18)",
    "Listen, my son, and be wise, and set your heart on the right path: Do not join those who drink too much wine or gorge themselves on meat, for drunkards and gluttons become poor, and drowsiness clothes them in rags. (Proverbs 23:19-21)",
    "Listen to your father, who gave you life, and do not despise your mother when she is old. (Proverbs 23:22)",
    "Buy the truth and do not sell it—wisdom, instruction and insight as well. (Proverbs 23:23)",
    "The father of a righteous child has great joy; a man who fathers a wise son rejoices in him. May your father and mother rejoice; may she who gave you birth be joyful! (Proverbs 23:24-25)",
    "My son, give me your heart and let your eyes delight in my ways, for an adulterous woman is a deep pit, and a wayward wife is a narrow well. Like a bandit she lies in wait and multiplies the unfaithful among men. (Proverbs 23:26-28)",
    "Who has woe? Who has sorrow? Who has strife? Who has complaints? Who has needless bruises? Who has bloodshot eyes? Those who linger over wine, who go to sample bowls of mixed wine. (Proverbs 23:29-30)",
    "Do not gaze at wine when it is red, when it sparkles in the cup, when it goes down smoothly! In the end it bites like a snake and poisons like a viper. (Proverbs 23:31-32)",
    "Your eyes will see strange sights, and your mind will imagine confusing things. You will be like one sleeping on the high seas, lying on top of the rigging. (Proverbs 23:33-34)",
    "They hit me,' you will say, 'but I'm not hurt! They beat me, but I don't feel it! When will I wake up so I can find another drink?' (Proverbs 23:35)",
    "Do not envy the wicked, do not desire their company; for their hearts plot violence, and their lips talk about making trouble. (Proverbs 24:1-2)",
    "By wisdom a house is built, and through understanding it is established; through knowledge its rooms are filled with rare and beautiful treasures. (Proverbs 24:3-4)",
    "The wise prevail through great power, and those who have knowledge muster their strength. Surely you need guidance to wage war, and victory is won through many advisers. (Proverbs 24:5-6)",
    "Wisdom is too high for fools; in the assembly at the gate they must not open their mouths. (Proverbs 24:7)"
]

def load_config():
    """Load configuration from config file or environment variables."""
    # Check for environment variables first (for GitHub Actions)
    if os.environ.get('SENDER_EMAIL') and os.environ.get('EMAIL_PASSWORD') and os.environ.get('RECIPIENT_EMAIL'):
        print("Using environment variables for configuration")
        
        # Parse recipient emails (can be comma-separated list)
        recipient_emails = [email.strip() for email in os.environ.get('RECIPIENT_EMAIL').split(',')]
        
        config = {
            "email": {
                "sender_email": os.environ.get('SENDER_EMAIL'),
                "sender_password": os.environ.get('EMAIL_PASSWORD'),
                "recipient_emails": recipient_emails,
                "smtp_server": os.environ.get('SMTP_SERVER', 'smtp.gmail.com'),
                "smtp_port": int(os.environ.get('SMTP_PORT', 587))
            },
            "last_sent_date": "",
            "sent_proverbs": []
        }
        
        # Try to load history from GITHUB_WORKSPACE if running in GitHub Actions
        if os.environ.get('GITHUB_WORKSPACE'):
            history_file = Path(os.environ['GITHUB_WORKSPACE']) / '.proverb_history.json'
            if history_file.exists():
                try:
                    with open(history_file, 'r') as f:
                        history = json.load(f)
                        config["last_sent_date"] = history.get("last_sent_date", "")
                        config["sent_proverbs"] = history.get("sent_proverbs", [])
                        print(f"Loaded proverb history from {history_file}")
                except Exception as e:
                    print(f"Warning: Could not load history file: {e}")
        # If not in GitHub Actions, try local config file
        elif os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    file_config = json.load(f)
                    config["last_sent_date"] = file_config.get("last_sent_date", "")
                    config["sent_proverbs"] = file_config.get("sent_proverbs", [])
            except Exception as e:
                print(f"Warning: Could not load tracking data from config file: {e}")
        
        return config
    
    # Otherwise, load from config file
    if not os.path.exists(CONFIG_FILE):
        # Default configuration
        config = {
            "email": {
                "sender_email": "",
                "sender_password": "",
                "recipient_emails": [""],
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587
            },
            "last_sent_date": "",
            "sent_proverbs": []
        }
        save_config(config)
        print(f"Created default config file at {CONFIG_FILE}")
        return config
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            
            # Handle backward compatibility with old config format
            if "recipient_email" in config["email"]:
                config["email"]["recipient_emails"] = [config["email"]["recipient_email"]]
                del config["email"]["recipient_email"]
            
            # Ensure recipient_emails is a list
            if not isinstance(config["email"]["recipient_emails"], list):
                config["email"]["recipient_emails"] = [config["email"]["recipient_emails"]]
                
            return config
    except Exception as e:
        print(f"Error loading config file: {e}")
        sys.exit(1)

def save_config(config):
    """Save configuration to config file and history if in GitHub Actions."""
    try:
        # Save to config file for local development
        if not os.environ.get('GITHUB_WORKSPACE'):
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"Configuration saved to {CONFIG_FILE}")
        
        # Save history to GITHUB_WORKSPACE for GitHub Actions
        if os.environ.get('GITHUB_WORKSPACE'):
            history_file = Path(os.environ['GITHUB_WORKSPACE']) / '.proverb_history.json'
            history = {
                "last_sent_date": config["last_sent_date"],
                "sent_proverbs": config["sent_proverbs"]
            }
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=4)
            print(f"Proverb history saved to {history_file}")
    except Exception as e:
        print(f"Error saving configuration: {e}")

def select_random_proverb(config):
    """Select a random proverb that hasn't been sent recently."""
    # If we've sent all proverbs, reset the list
    if len(config["sent_proverbs"]) >= len(PROVERBS):
        print("All proverbs have been sent. Resetting the list.")
        config["sent_proverbs"] = []
    
    # Get proverbs that haven't been sent yet
    available_proverbs = [p for i, p in enumerate(PROVERBS) if i not in config["sent_proverbs"]]
    
    # Select a random proverb
    proverb = random.choice(available_proverbs)
    
    # Record that we've sent this proverb
    proverb_index = PROVERBS.index(proverb)
    config["sent_proverbs"].append(proverb_index)
    
    return proverb, proverb_index + 1  # Add 1 to make it 1-based instead of 0-based

def send_email(config, proverb, proverb_number):
    """Send an email with the proverb to all recipients."""
    sender_email = config["email"]["sender_email"]
    password = config["email"]["sender_password"]
    recipient_emails = config["email"]["recipient_emails"]
    smtp_server = config["email"]["smtp_server"]
    smtp_port = config["email"]["smtp_port"]
    
    if not recipient_emails:
        print("No recipient emails specified. Cannot send email.")
        return False
    
    # Create message
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Proverb #{proverb_number} - {datetime.datetime.now().strftime('%Y-%m-%d')}"
    message["From"] = sender_email
    message["To"] = ", ".join(recipient_emails)  # Join all recipients with commas
    
    # Create HTML version of the message
    html = f"""
    <html>
      <body>
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
          <h2 style="color: #333; border-bottom: 1px solid #ddd; padding-bottom: 10px;">Proverb #{proverb_number} - {datetime.datetime.now().strftime('%Y-%m-%d')}</h2>
          <p style="font-size: 18px; line-height: 1.6; color: #555; margin: 20px 0; padding: 15px; background-color: #f9f9f9; border-left: 4px solid #4CAF50; font-style: italic;">
            {proverb}
          </p>
          <p style="color: #777; font-size: 14px; text-align: center; margin-top: 30px;">
            Sent on {datetime.datetime.now().strftime('%A, %B %d, %Y')}
          </p>
        </div>
      </body>
    </html>
    """
    
    # Turn these into plain/html MIMEText objects
    part = MIMEText(html, "html")
    
    # Add HTML part to MIMEMultipart message
    message.attach(part)
    
    # Create secure connection with server and send email
    context = ssl.create_default_context()
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient_emails, message.as_string())
        print(f"Email sent successfully to {', '.join(recipient_emails)}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    finally:
        try:
            server.quit()
        except:
            pass

def main():
    print(f"Daily Proverb Emailer - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load configuration
    config = load_config()
    
    # Check if we need to configure the email settings
    if not config["email"]["sender_email"] or not config["email"]["recipient_emails"]:
        print("Email configuration is missing. Please update the config.json file or set environment variables.")
        print("Required environment variables: SENDER_EMAIL, EMAIL_PASSWORD, RECIPIENT_EMAIL")
        print("Optional environment variables: SMTP_SERVER, SMTP_PORT")
        return 1
    
    # Check if we've already sent a proverb today
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    if config["last_sent_date"] == today:
        print(f"Already sent a proverb today ({today}). Skipping.")
        return 0
    
    # Select a random proverb
    proverb, proverb_number = select_random_proverb(config)
    print(f"Selected proverb #{proverb_number}: {proverb[:50]}...")
    
    # Send the email
    success = send_email(config, proverb, proverb_number)
    
    # Update the last sent date if successful
    if success:
        config["last_sent_date"] = today
        save_config(config)
        print(f"Proverb #{proverb_number} sent and config updated. Next proverb will be sent tomorrow.")
        return 0
    else:
        print("Failed to send email. Configuration not updated.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
