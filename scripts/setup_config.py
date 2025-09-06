#!/usr/bin/env python3
import json
import os
import sys

def main():
    try:
        # Get recipients as list
        recipients = [r.strip() for r in os.environ.get("RECIPIENTS", "").split(",") if r.strip()]
        
        # Create config
        data = {
            "twilio": {
                "account_sid": os.environ["TWILIO_ACCOUNT_SID"],
                "auth_token": os.environ["TWILIO_AUTH_TOKEN"],
                "phone_number": os.environ["TWILIO_PHONE_NUMBER"]
            },
            "recipients": recipients,
            "history_size": 7,
            "history": []
        }
        
        # Write to file
        with open("config.json", "w") as f:
            json.dump(data, f, indent=2)
            
        # Verify it can be read back
        with open("config.json") as f:
            json.load(f)
            
        print("Config file created and validated successfully")
        
        # Print config (with sensitive data masked)
        if "twilio" in data and "auth_token" in data["twilio"]:
            data["twilio"]["auth_token"] = "***MASKED***"
        print("Config content:")
        print(json.dumps(data, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"Error creating config: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
