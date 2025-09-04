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
            "gvoice": {
                "email": os.environ["GVOICE_EMAIL"],
                "password": os.environ["GVOICE_PASSWORD"],
                "number": os.environ["GVOICE_NUMBER"]
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
        if "gvoice" in data and "password" in data["gvoice"]:
            data["gvoice"]["password"] = "***MASKED***"
        print("Config content:")
        print(json.dumps(data, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"Error creating config: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
