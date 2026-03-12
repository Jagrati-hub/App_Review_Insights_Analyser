# Email Integration Troubleshooting Guide

## Issue: Emails Not Being Sent

### Problem
Email drafts are being saved to files, but emails are not being sent to the recipient's inbox.

### Root Cause
The `.env` file had incorrect variable names for SMTP credentials:
- **Wrong**: `email_sender` and `email_password`
- **Correct**: `SMTP_USERNAME` and `SMTP_PASSWORD`

### Solution Applied

#### 1. Fixed `.env` File
Updated the SMTP configuration in `.env`:

```env
# SMTP Email Configuration (for sending reports via Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=manshuc@gmail.com
SMTP_PASSWORD=knakwswgklmlogcd
SENDER_EMAIL=manshuc@gmail.com
SENDER_NAME=Groww Product Team
```

#### 2. Verified Email Sending Works
Ran test script successfully:
```bash
python test_smtp.py
```

Result: ✅ Email sent successfully to manshuc12@gmail.com

---

## How to Verify Email Integration is Working

### Step 1: Test Email Sending
Run the test script to verify SMTP credentials work:

```bash
python test_smtp.py
```

Expected output:
```
============================================================
SMTP EMAIL TEST
============================================================

Testing email to: manshuc12@gmail.com

============================================================
RESULT
============================================================
✅ Email sent: True
📁 Draft saved: phase5/drafts/email_draft_YYYYMMDD_HHMMSS.txt
📧 Recipient: manshuc12@gmail.com
============================================================

✅ SUCCESS! Check your inbox at manshuc12@gmail.com
(Also check spam folder)
```

### Step 2: Restart the Scheduler
**IMPORTANT**: The scheduler must be restarted to pick up the new SMTP credentials.

1. Stop the current scheduler (press Ctrl+C in the terminal)
2. Restart it:
   ```bash
   python phase6/scheduler.py
   ```
   Or use the batch file:
   ```bash
   start-scheduler.bat
   ```

### Step 3: Check Scheduler Logs
After the scheduler runs (every 5 minutes), check the logs:

```bash
# View last 50 lines of scheduler log
Get-Content phase6/logs/scheduler.log | Select-Object -Last 50
```

Look for these log messages indicating successful email sending:
```
phase5.email_drafter - INFO - Connecting to SMTP server: smtp.gmail.com:587
phase5.email_drafter - INFO - Logging in as: manshuc@gmail.com
phase5.email_drafter - INFO - Sending email to: manshuc12@gmail.com
phase5.email_drafter - INFO - Email sent successfully to manshuc12@gmail.com
phase5.email_drafter - INFO - ✅ Email sent successfully to manshuc12@gmail.com
```

### Step 4: Check Your Inbox
1. Check inbox at **manshuc12@gmail.com**
2. Also check **Spam/Junk folder** (Gmail may filter automated emails)
3. Look for emails with subject: "Play Store Pulse Report - Week of [date] to [date]"

---

## Email Flow in the System

### 1. Scheduler (Every 5 Minutes)
- `phase6/scheduler.py` runs every 5 minutes
- Creates an `AnalysisRequest` with recipient email
- Calls `PipelineOrchestrator.run_pipeline()`

### 2. Pipeline Orchestrator
- `phase2/pipeline_orchestrator.py` coordinates all phases
- Phase 5: Calls `EmailDrafter.draft_email()`

### 3. Email Drafter
- `phase5/email_drafter.py` handles email creation and sending
- Saves draft to file (backup)
- Sends email via SMTP if credentials are configured
- Logs success/failure

### 4. Configuration
- `common/config.py` loads SMTP settings from `.env`
- Required variables:
  - `SMTP_SERVER` (default: smtp.gmail.com)
  - `SMTP_PORT` (default: 587 for TLS)
  - `SMTP_USERNAME` (your Gmail address)
  - `SMTP_PASSWORD` (Gmail App Password)
  - `SENDER_EMAIL` (defaults to SMTP_USERNAME)
  - `SENDER_NAME` (default: Groww Product Team)

---

## Common Issues and Solutions

### Issue 1: No Email Logs in Scheduler
**Symptom**: Scheduler logs show "Email draft saved" but no "Email sent successfully"

**Cause**: Scheduler was started before `.env` was fixed

**Solution**: Restart the scheduler to reload configuration

### Issue 2: SMTP Authentication Failed
**Symptom**: Error message "SMTP authentication failed"

**Causes**:
- Using regular Gmail password instead of App Password
- Incorrect App Password
- 2-Factor Authentication not enabled

**Solution**: 
1. Enable 2FA on Gmail account
2. Generate new App Password at https://myaccount.google.com/apppasswords
3. Update `SMTP_PASSWORD` in `.env`
4. Restart scheduler

### Issue 3: Emails Going to Spam
**Symptom**: Emails sent successfully but not in inbox

**Solution**: 
1. Check Spam/Junk folder
2. Mark email as "Not Spam"
3. Add sender to contacts
4. Create filter to always deliver to inbox

### Issue 4: Connection Timeout
**Symptom**: Error message "Connection timed out"

**Causes**:
- Firewall blocking port 587
- Network restrictions
- Gmail SMTP temporarily unavailable

**Solution**:
1. Check firewall settings
2. Try port 465 (SSL) instead of 587 (TLS)
3. Update `.env`: `SMTP_PORT=465`
4. Restart scheduler

---

## Verification Checklist

- [ ] `.env` file has correct SMTP variable names
- [ ] `SMTP_USERNAME` is your Gmail address
- [ ] `SMTP_PASSWORD` is a Gmail App Password (not regular password)
- [ ] Test script (`test_smtp.py`) runs successfully
- [ ] Scheduler has been restarted after `.env` changes
- [ ] Scheduler logs show "Email sent successfully" messages
- [ ] Email received in inbox (or spam folder)

---

## Quick Test Commands

```bash
# Test SMTP credentials
python test_smtp.py

# Run scheduler once (test mode)
python phase6/scheduler.py --test

# View recent scheduler logs
Get-Content phase6/logs/scheduler.log | Select-Object -Last 50

# Check recent email drafts
Get-ChildItem phase5/drafts | Sort-Object LastWriteTime -Descending | Select-Object -First 5
```

---

## Files Modified

1. **`.env`** - Fixed SMTP variable names
2. **`test_smtp.py`** - Created simple test script
3. **`phase5/test_email.py`** - Fixed to create 3 themes (required by PulseReport)

---

## Next Steps

1. **Restart the scheduler** to apply the SMTP configuration changes
2. **Wait 5 minutes** for the next scheduled run
3. **Check the logs** for "Email sent successfully" message
4. **Check your inbox** at manshuc12@gmail.com (and spam folder)

If emails are still not arriving after following these steps, run the test script again and share any error messages.
