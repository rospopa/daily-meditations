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
            "email": {
                "smtp_server": "smtp.gmail.com",
                "port": 587,
                "sender_email": "your-email@gmail.com",
                "password": "your-app-specific-password",
                "subject": "Daily Meditation"
            },
            "recipients": ["recipient@example.com"],
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

def send_email(config, meditation, meditation_number):
    """Send an email with the daily meditation to all recipients."""
    email_config = config["email"]
    
    # Create message
    message = MIMEMultipart("alternative")
    message["Subject"] = f"{email_config['subject']} #{meditation_number}"
    message["From"] = email_config["sender_email"]
    message["To"] = ", ".join(config["recipients"])
    
    # Create HTML content
    html = f"""\
    <html>
      <body>
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
          <h2 style="color: #333366;">Your Daily Meditation</h2>
          <div style="background-color: #f9f9f9; padding: 20px; border-left: 5px solid #6666cc; margin: 20px 0;">
            <p style="font-style: italic; font-size: 1.2em; line-height: 1.6;">{meditation}</p>
          </div>
          <p style="color: #666666; font-size: 0.9em;">
            Meditation #{meditation_number} • {date}
          </p>
          <p style="color: #999999; font-size: 0.8em; margin-top: 30px;">
            To unsubscribe or update your preferences, please reply to this email.
          </p>
        </div>
      </body>
    </html>
    """.format(meditation=meditation, 
               date=datetime.datetime.now().strftime("%B %d, %Y"))
    
    # Attach HTML content
    part = MIMEText(html, "html")
    message.attach(part)
    
    # Send email
    context = ssl.create_default_context()
    with smtplib.SMTP(email_config["smtp_server"], email_config["port"]) as server:
        server.starttls(context=context)
        server.login(email_config["sender_email"], email_config["password"])
        server.sendmail(
            email_config["sender_email"], 
            config["recipients"], 
            message.as_string()
        )

def main():
    """Main function to send daily meditation."""
    try:
        # Load configuration
        config = load_config()
        
        # Select a random meditation
        meditation, meditation_number = select_random_meditation(config)
        
        # Send email
        send_email(config, meditation, meditation_number)
        print(f"Successfully sent meditation #{meditation_number}")
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
