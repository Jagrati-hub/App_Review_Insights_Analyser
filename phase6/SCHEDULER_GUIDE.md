# Weekly Pulse Scheduler Guide

The automated scheduler generates weekly pulse reports every week at 1:00 PM IST and sends them to manshuc12@gmail.com.

## Features

- **Automated Execution**: Runs every week at 1:00 PM IST
- **Fixed Recipient**: Reports sent to manshuc12@gmail.com
- **Configurable Analysis Window**: Default 10 weeks of reviews
- **Automatic Archiving**: Saves reports to `phase6/reports/`
- **Comprehensive Logging**: Logs to `phase6/scheduler.log`
- **Error Handling**: Continues running even if a report generation fails

## Quick Start

### Option 1: Using Batch Script (Recommended)

```bash
start-scheduler.bat
```

This will start the scheduler and keep it running in the background.

### Option 2: Manual Start

```bash
# Activate virtual environment
venv\Scripts\activate

# Start scheduler
python phase6/scheduler.py
```

## Testing the Scheduler

To test the scheduler without waiting for the scheduled time:

```bash
test-scheduler.bat
```

Or manually:

```bash
python phase6/scheduler.py --test
```

This will generate a report immediately and save it to `phase6/reports/`.

## Configuration

### Default Settings

- **Schedule**: Every week at 1:00 PM IST
- **Recipient**: manshuc12@gmail.com
- **Analysis Window**: 10 weeks
- **Timezone**: Asia/Kolkata (IST)

### Custom Configuration

You can customize the scheduler using command-line arguments:

```bash
# Custom recipient email
python phase6/scheduler.py --email your.email@example.com

# Custom schedule time (24-hour format)
python phase6/scheduler.py --time 14:30

# Custom analysis window
python phase6/scheduler.py --weeks 12

# Combine multiple options
python phase6/scheduler.py --email team@example.com --time 09:00 --weeks 8
```

## Output Files

The scheduler creates two types of files in `phase6/reports/`:

1. **Report JSON**: `weekly_pulse_YYYYMMDD_HHMMSS.json`
   - Complete report data including themes, quotes, and action ideas
   - Metadata about the analysis

2. **Email Draft**: `email_draft_YYYYMMDD_HHMMSS.txt`
   - Formatted email ready to send
   - Includes all report sections

## Logs

The scheduler maintains a log file at `phase6/scheduler.log` with:

- Execution timestamps
- Success/failure status
- Error messages and stack traces
- Next scheduled run time

### Viewing Logs

```bash
# View recent logs
type phase6\scheduler.log

# View last 50 lines
powershell -Command "Get-Content phase6\scheduler.log -Tail 50"

# Monitor logs in real-time
powershell -Command "Get-Content phase6\scheduler.log -Wait"
```

## Running as a Background Service

### Option 1: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Weekly, every week at 1:00 PM
4. Set action: Start a program
5. Program: `C:\path\to\start-scheduler.bat`

### Option 2: Keep Terminal Open

Simply run `start-scheduler.bat` and minimize the window. The scheduler will continue running.

### Option 3: Use nohup (if using WSL/Linux)

```bash
nohup python phase6/scheduler.py > scheduler.out 2>&1 &
```

## Monitoring

### Check if Scheduler is Running

```bash
# Windows
tasklist | findstr python

# Check logs for recent activity
type phase6\scheduler.log
```

### Check Next Run Time

The scheduler logs the next scheduled run time after each execution. Check the log file:

```bash
type phase6\scheduler.log | findstr "Next run"
```

## Troubleshooting

### Scheduler Not Running

**Problem**: Scheduler stops unexpectedly

**Solutions**:
1. Check `phase6/scheduler.log` for errors
2. Ensure virtual environment is activated
3. Verify all dependencies are installed: `pip install -r requirements.txt`
4. Check if Groq API key is valid in `.env`

### Reports Not Generated

**Problem**: Scheduler runs but no reports are created

**Solutions**:
1. Check `phase6/scheduler.log` for error messages
2. Verify internet connection (needed for scraping)
3. Test manually: `python phase6/scheduler.py --test`
4. Check if `phase6/reports/` directory exists and is writable

### Wrong Timezone

**Problem**: Scheduler runs at wrong time

**Solution**: The scheduler uses IST (Asia/Kolkata) by default. To change:

```python
# Edit phase6/scheduler.py
scheduler = WeeklyPulseScheduler(
    timezone="America/New_York"  # Change to your timezone
)
```

### Email Not Sent

**Note**: The current implementation generates email drafts but doesn't send them automatically. To enable automatic sending, you'll need to:

1. Configure SMTP settings in `.env`
2. Implement email sending in `phase5/email_drafter.py`
3. Update scheduler to trigger email sending

## Advanced Usage

### Multiple Schedules

To run multiple schedules (e.g., different recipients or times):

```bash
# Terminal 1: Weekly report for team
python phase6/scheduler.py --email team@example.com --time 09:00

# Terminal 2: Weekly report for management
python phase6/scheduler.py --email management@example.com --time 14:00
```

### Custom Schedule Patterns

Edit `phase6/scheduler.py` to customize the schedule:

```python
# Every day at 2 PM
schedule.every().day.at("14:00").do(self.generate_weekly_pulse)

# Every Monday at 9 AM
schedule.every().monday.at("09:00").do(self.generate_weekly_pulse)

# Every 3 days
schedule.every(3).days.at("10:00").do(self.generate_weekly_pulse)
```

## Integration with Web UI

The scheduler runs independently of the web UI. Both can run simultaneously:

- **Web UI**: Manual, on-demand report generation
- **Scheduler**: Automated, scheduled report generation

To run both:

```bash
# Terminal 1: Start web servers
start-all.bat

# Terminal 2: Start scheduler
start-scheduler.bat
```

## Performance Considerations

- **Execution Time**: Each report takes 3-7 minutes to generate
- **Resource Usage**: Minimal CPU/memory when idle, moderate during generation
- **API Limits**: Respects Groq API rate limits with retry logic
- **Storage**: Each report is ~50-100 KB

## Security Notes

1. **API Keys**: Ensure `.env` file is not committed to git
2. **Email Address**: Hardcoded recipient prevents unauthorized access
3. **Logs**: May contain sensitive data, restrict access to `phase6/scheduler.log`
4. **Reports**: Stored locally, ensure proper file permissions

## Support

For issues or questions:
1. Check `phase6/scheduler.log` for errors
2. Test manually with `test-scheduler.bat`
3. Review this guide
4. Check main `README.md` for general setup

## Example Log Output

```
2026-03-13 13:00:00 - scheduler - INFO - ============================================================
2026-03-13 13:00:00 - scheduler - INFO - Starting scheduled weekly pulse generation
2026-03-13 13:00:00 - scheduler - INFO - ============================================================
2026-03-13 13:00:00 - scheduler - INFO - Request ID: req_20260313_130000_abc123
2026-03-13 13:00:00 - scheduler - INFO - Analyzing reviews from past 10 weeks
2026-03-13 13:05:23 - scheduler - INFO - ✅ Weekly pulse generated successfully!
2026-03-13 13:05:23 - scheduler - INFO - Report ID: req_20260313_130000_abc123
2026-03-13 13:05:23 - scheduler - INFO - Reviews analyzed: 1042
2026-03-13 13:05:23 - scheduler - INFO - Report saved to: phase6/reports/weekly_pulse_20260313_130523.json
2026-03-13 13:05:23 - scheduler - INFO - Email draft saved to: phase6/reports/email_draft_20260313_130523.txt
2026-03-13 13:05:23 - scheduler - INFO - ============================================================
2026-03-13 13:05:23 - scheduler - INFO - Next run scheduled for: 2026-03-20 13:00:00 IST
2026-03-13 13:05:23 - scheduler - INFO - ============================================================
```
