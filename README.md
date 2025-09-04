# Daily Meditation Emailer

This Python script sends a daily inspirational meditation or quote to your email address.

## Features

- Sends a thoughtful daily meditation or quote
- Tracks which meditations have been sent to avoid repetition
- Beautifully formatted HTML email
- Only sends one proverb per day
- Easy to configure
- Can run locally or via GitHub Actions
- Supports multiple recipients

## Setup Instructions

### Local Setup

1. **Edit the configuration file:**
   
   Open `config.json` and fill in your email information:
   ```json
   {
       "email": {
           "smtp_server": "smtp.gmail.com",
           "port": 587,
           "sender_email": "your-email@gmail.com",
           "password": "your-app-specific-password",
           "subject": "Daily Meditation"
       },
       "recipients": ["recipient1@example.com", "recipient2@example.com"],
       "history_size": 30,
       "history": []
   }
   ```

   **Important Note for Gmail Users:** 
   - If you're using Gmail, you'll need to use an "App Password" instead of your regular password
   - To create an App Password:
     1. Enable 2-Step Verification on your Google Account
     2. Go to your Google Account → Security → App passwords
     3. Select "Mail" and your device, then generate
     4. Use the 16-character code as your password in the config file

2. **Run the script manually:**
   ```
   python daily_meditation.py
   ```

3. **Schedule the script to run daily:**

   **On Windows:**
   - Open Task Scheduler
   - Create a new Basic Task
   - Set it to run daily at your preferred time
   - For the action, select "Start a program"
   - Browse to select `schedule_task.bat`
   - Make sure to update the batch file to point to `daily_meditation.py`

   **On macOS/Linux:**
   Use cron to schedule the script. Run `crontab -e` and add:
   ```
   0 9 * * * cd /path/to/daily-meditations && python3 daily_meditation.py
   ```
   (This will run at 9 AM daily - adjust the time as needed)

### GitHub Actions Setup

1. **Fork this repository** to your GitHub account

2. **Add the following secrets** in your repository settings (Settings > Secrets > Actions):
   - `SENDER_EMAIL`: Your email address
   - `SENDER_PASSWORD`: Your email password (or app password for Gmail)
   - `RECIPIENTS`: Comma-separated list of recipient email addresses
   - `SMTP_SERVER`: Your SMTP server (e.g., `smtp.gmail.com`)
   - `SMTP_PORT`: Your SMTP port (e.g., `587` for Gmail)

3. **The workflow will run daily at 8:00 AM UTC**
   - You can also manually trigger it from the Actions tab

4. **First Run:**
   - After setting up the secrets, go to the "Actions" tab
   - Select the "Daily Meditation Email" workflow
   - Click "Run workflow" to test it

## Adding More Recipients

You can add multiple recipients to receive the daily meditations:

### For Local Setup:
Edit your `config.json` file and update the `recipients` field to include an array of email addresses:
```json
"recipients": ["person1@example.com", "person2@example.com", "person3@example.com"]
```

### For GitHub Actions:
Update the `RECIPIENTS` secret in your GitHub repository:
1. Go to your repository's "Settings" > "Secrets and variables" > "Actions"
2. Edit the `RECIPIENTS` secret
3. Enter multiple email addresses separated by commas (no spaces):
   ```
   email1@example.com,email2@example.com,email3@example.com
   ```

## Customizing the Meditations

You can edit the `daily_meditation.py` file to modify the list of meditations or customize the email content. The meditations are stored in the `MEDITATIONS` list at the top of the file.

## Troubleshooting

- If emails aren't being sent, check your SMTP settings and credentials
- For Gmail, make sure you're using an App Password, not your regular password
- Check that your email provider allows SMTP access
- If using GitHub Actions, verify your secrets are set correctly
- Check the GitHub Actions logs for any error messages
