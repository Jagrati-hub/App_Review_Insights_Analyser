# Email Sending Setup Guide

This guide explains how to configure email sending for automated pulse reports.

## Overview

The system now sends emails automatically via SMTP (Gmail) instead of just saving drafts. Emails are sent to the configured recipient after each report generation.

## Gmail SMTP Setup

### Step 1: Enable 2-Factor Authentication

1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to **Security**
3. Enable **2-Step Verification** if not already enabled

### Step 2: Generate App Password

**Important**: You cannot use your regular Gmail password for SMTP. You must create an App Password.

1. Go to https://myaccount.google.com/apppasswords
2. Select app: **Mail**
3. Select device: **Other (Custom name)**
4. Enter name: **Play Store Analyzer**
5. Click **Generate**
6. Copy the 16-character password (remove spaces)

### Step 3: Configure Environment Variables

Add the following to your `.env` file:

```env
# SMTP Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
SENDER_EMAIL=your_email@gmail.com
SENDER_NAME=Groww Product Team
```

**Example:**
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=manshuc12@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
SENDER_EMAIL=manshuc12@gmail.com
SENDER_NAME=Groww Product Team
```

### Step 4: Test Email Sending

Run a test to verify email sending works:

```bash
python phase5/test_email.py
```

Or generate a report manually:

```bash
test-scheduler.bat
```

Check your inbox (and spam folder) for the email.

## Configuration Options

### SMTP Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `SMTP_SERVER` | SMTP server address | smtp.gmail.com |
| `SMTP_PORT` | SMTP port (587=TLS, 465=SSL) | 587 |
| `SMTP_USERNAME` | Your Gmail address | (required) |
| `SMTP_PASSWORD` | Gmail app password | (required) |
| `SENDER_EMAIL` | From email address | Same as SMTP_USERNAME |
| `SENDER_NAME` | Display name in emails | Groww Product Team |

### Port Options

- **587**: TLS (recommended for Gmail)
- **465**: SSL (alternative)
- **25**: Plain (not recommended)

## Troubleshooting

### Authentication Failed

**Error**: "SMTP authentication failed"

**Solutions:**
1. Verify you're using an **App Password**, not your regular password
2. Check that 2-Factor Authentication is enabled
3. Regenerate the App Password
4. Remove spaces from the App Password
5. Verify the email address is correct

### Connection Timeout

**Error**: "Connection timed out"

**Solutions:**
1. Check your internet connection
2. Verify SMTP server and port
3. Check firewall settings
4. Try port 465 instead of 587

### Email Not Received

**Check:**
1. Spam/Junk folder
2. Gmail "Sent" folder (to verify it was sent)
3. Recipient email address is correct
4. Check logs in `phase6/logs/scheduler.log`

### Less Secure Apps

**Note**: Gmail no longer supports "Less Secure Apps". You MUST use App Passwords.

If you see this error, enable 2FA and create an App Password.

## Using Other Email Providers

### Outlook/Hotmail

```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your_email@outlook.com
SMTP_PASSWORD=your_password
```

### Yahoo Mail

```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=your_email@yahoo.com
SMTP_PASSWORD=your_app_password
```

### Custom SMTP Server

```env
SMTP_SERVER=mail.yourdomain.com
SMTP_PORT=587
SMTP_USERNAME=your_email@yourdomain.com
SMTP_PASSWORD=your_password
```

## Email Format

### Subject Line

```
Play Store Pulse Report - Week of Mar 06 to Mar 13, 2026
```

### Email Body

```
Hi Team,

Here's your weekly pulse report based on 1,042 Google Play Store reviews from March 06 to March 13, 2026.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 TOP THEMES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. High Brokerage Charges (783 reviews)
   Users are concerned about the high brokerage fees...

2. Technical Issues (767 reviews)
   Users report app crashes and login problems...

3. Ease of Use (717 reviews)
   Users appreciate the simple and intuitive interface...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 USER VOICES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. "The brokerage charges are too high compared to other platforms..."

2. "App crashes frequently when I try to place orders..."

3. "Very easy to use, perfect for beginners..."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 ACTION IDEAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Consider implementing a tiered pricing structure...

2. Prioritize fixing critical bugs causing app crashes...

3. Maintain the simple UI while adding advanced features...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Best regards,
Groww Product Team

Report generated: 2026-03-13 15:30:00
Word count: 245
```

## Disabling Email Sending

If you want to save drafts only without sending emails:

### Option 1: Remove SMTP Credentials

Remove or comment out SMTP settings in `.env`:

```env
# SMTP_USERNAME=
# SMTP_PASSWORD=
```

The system will save drafts but skip email sending.

### Option 2: Modify Code

Edit `phase5/email_drafter.py`:

```python
def __init__(self, output_dir: Optional[str] = None, send_email: bool = False):
    # Change send_email default to False
```

## Security Best Practices

### 1. Protect Your Credentials

- ✅ Never commit `.env` file to git
- ✅ Use App Passwords, not regular passwords
- ✅ Rotate passwords periodically
- ✅ Limit access to `.env` file

### 2. Email Security

- ✅ Use TLS/SSL encryption (port 587 or 465)
- ✅ Verify recipient email addresses
- ✅ Monitor sent emails for anomalies
- ✅ Set up email alerts for failures

### 3. Access Control

- ✅ Restrict who can modify SMTP settings
- ✅ Use separate email accounts for automation
- ✅ Enable audit logging
- ✅ Review email logs regularly

## Monitoring

### Check Email Status

Logs show email sending status:

```
2026-03-13 15:30:00 - phase5.email_drafter - INFO - Connecting to SMTP server: smtp.gmail.com:587
2026-03-13 15:30:01 - phase5.email_drafter - INFO - Logging in as: manshuc12@gmail.com
2026-03-13 15:30:02 - phase5.email_drafter - INFO - Sending email to: recipient@example.com
2026-03-13 15:30:03 - phase5.email_drafter - INFO - ✅ Email sent successfully to recipient@example.com
```

### View Logs

```bash
# View scheduler logs
view-scheduler-logs.bat

# Or directly
type phase6\logs\scheduler.log | findstr "email"
```

### Verify Sent Emails

1. Check Gmail "Sent" folder
2. Check recipient inbox
3. Review logs for confirmation
4. Check draft files in `phase5/drafts/`

## Testing

### Test Email Configuration

Create `phase5/test_email.py`:

```python
from email_drafter import EmailDrafter
from common.models import PulseReport, Theme, Review
from datetime import datetime, date

# Create test report
report = PulseReport(
    date_range=(date(2026, 3, 6), date(2026, 3, 13)),
    themes=[],
    quotes=["Test quote"],
    action_ideas=["Test action"],
    word_count=10,
    review_count=100,
    generation_timestamp=datetime.now()
)

# Send test email
drafter = EmailDrafter(send_email=True)
content, metadata = drafter.draft_email(
    report=report,
    recipient="your_test_email@example.com"
)

print(f"Email sent: {metadata.email_sent}")
```

Run:
```bash
python phase5/test_email.py
```

## FAQ

### Q: Do I need a Gmail account?

A: No, you can use any SMTP server. Gmail is recommended for ease of setup.

### Q: Can I send to multiple recipients?

A: Currently, one recipient per report. To send to multiple, modify the code or use email forwarding.

### Q: Are emails sent for every report?

A: Yes, emails are sent automatically after each successful report generation.

### Q: What if email sending fails?

A: The draft is still saved. Check logs for error details. The pipeline continues even if email fails.

### Q: Can I customize the email template?

A: Yes, edit `phase5/email_drafter.py` methods `_format_subject()` and `_format_body()`.

### Q: Is my password secure?

A: Yes, if you use App Passwords and keep `.env` file private. Never commit `.env` to git.

## Support

For issues:
1. Check this guide
2. Review logs in `phase6/logs/scheduler.log`
3. Test with `test_email.py`
4. Verify Gmail settings
5. Check spam folder

## Summary

✅ Email sending now works automatically
✅ Uses Gmail SMTP with App Passwords
✅ Emails sent after each report generation
✅ Drafts still saved as backup
✅ Comprehensive logging
✅ Secure configuration via .env
✅ Easy to test and troubleshoot

---

**Setup Time**: ~5 minutes
**Difficulty**: Easy
**Requirements**: Gmail account with 2FA enabled
