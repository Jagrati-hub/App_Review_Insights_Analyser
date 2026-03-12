# Scheduler Update - 180 Minute Interval

## Overview
Updated the scheduler to run every 180 minutes (3 hours) instead of every 5 minutes. This provides a more reasonable cadence for pulse reports while still maintaining regular updates.

## Changes Made

### 1. Scheduler Configuration (`phase6/scheduler.py`)

**Before**: Every 5 minutes
**After**: Every 180 minutes (3 hours)

```python
# Default interval changed from 5 to 180
schedule_interval: int = 180  # Run every 180 minutes (3 hours)
```

### 2. Run Times (IST - India Standard Time)

The scheduler will run at these times every day:
- **00:00** (Midnight)
- **03:00** (3 AM)
- **06:00** (6 AM)
- **09:00** (9 AM)
- **12:00** (Noon)
- **15:00** (3 PM)
- **18:00** (6 PM)
- **21:00** (9 PM)

**Total**: 8 reports per day

### 3. Startup Script (`start-scheduler.bat`)

Updated to show the new schedule:
```batch
Schedule: Every 180 minutes (3 hours)
Run times: 00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00 IST
```

### 4. GitHub Actions (`.github/workflows/scheduled-pulse-report.yml`)

Updated cron schedule:
```yaml
# Before
cron: '*/5 * * * *'  # Every 5 minutes

# After
cron: '0 */3 * * *'  # Every 3 hours at the top of the hour
```

**Note**: GitHub Actions uses UTC time, so the actual IST times will be offset by +5:30 hours.

## Benefits of 180-Minute Interval

### 1. More Reasonable Cadence
- 8 reports per day instead of 288
- Reduces noise and email fatigue
- More time for meaningful review changes to accumulate

### 2. Resource Efficiency
- Less API calls to Groq
- Reduced server load
- Lower bandwidth usage
- Fewer emails sent

### 3. Better Data Quality
- More reviews accumulated between runs
- More significant trends visible
- Better statistical significance

### 4. Cost Savings
- Fewer Groq API calls (saves on API costs)
- Less storage for reports
- Reduced email sending costs

## How to Use

### Start the Scheduler

**Option 1: Using batch file**
```bash
start-scheduler.bat
```

**Option 2: Direct Python command**
```bash
python phase6/scheduler.py
```

**Option 3: Custom interval**
```bash
# Run every 60 minutes (1 hour)
python phase6/scheduler.py --interval 60

# Run every 360 minutes (6 hours)
python phase6/scheduler.py --interval 360
```

### Test Mode (Run Once)
```bash
python phase6/scheduler.py --test
```

### Custom Configuration
```bash
python phase6/scheduler.py --interval 180 --email your@email.com --weeks 10
```

## Verification

### Check Scheduler Logs
```bash
# View last 50 lines
Get-Content phase6/logs/scheduler.log | Select-Object -Last 50
```

Look for:
```
Scheduler initialized:
  - Schedule: Every 180 minutes (3 hours)
  - Run times: 00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00 IST
```

### Monitor Next Run Time
The scheduler logs show the next scheduled run time:
```
Next run scheduled for: 2026-03-13 15:00:00 IST
```

## Customization

### Change Interval

Edit `phase6/scheduler.py`:
```python
def __init__(
    self,
    recipient_email: str = "manshuc12@gmail.com",
    schedule_interval: int = 180,  # Change this value
    timezone: str = "Asia/Kolkata",
    weeks_back: int = 10
):
```

Common intervals:
- **60 minutes** = 1 hour (24 reports/day)
- **120 minutes** = 2 hours (12 reports/day)
- **180 minutes** = 3 hours (8 reports/day) ← Current
- **240 minutes** = 4 hours (6 reports/day)
- **360 minutes** = 6 hours (4 reports/day)
- **720 minutes** = 12 hours (2 reports/day)
- **1440 minutes** = 24 hours (1 report/day)

### Change Run Times

For specific times (e.g., only business hours), modify the `start()` method:

```python
# Run at specific times instead of intervals
schedule.every().day.at("09:00").do(self.generate_weekly_pulse)
schedule.every().day.at("15:00").do(self.generate_weekly_pulse)
schedule.every().day.at("21:00").do(self.generate_weekly_pulse)
```

## GitHub Actions Schedule

### Current Schedule (UTC)
```yaml
cron: '0 */3 * * *'  # Every 3 hours
```

This runs at:
- 00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00 UTC

### IST Conversion
UTC to IST = +5:30 hours

So GitHub Actions runs at these IST times:
- 05:30, 08:30, 11:30, 14:30, 17:30, 20:30, 23:30, 02:30 IST

### Align with IST Times

To run at exact IST times (00:00, 03:00, etc.), adjust the cron:

```yaml
# For 00:00 IST (18:30 UTC previous day)
cron: '30 18,21,0,3,6,9,12,15 * * *'
```

Or use multiple cron expressions:
```yaml
schedule:
  - cron: '30 18 * * *'  # 00:00 IST
  - cron: '30 21 * * *'  # 03:00 IST
  - cron: '30 0 * * *'   # 06:00 IST
  - cron: '30 3 * * *'   # 09:00 IST
  - cron: '30 6 * * *'   # 12:00 IST
  - cron: '30 9 * * *'   # 15:00 IST
  - cron: '30 12 * * *'  # 18:00 IST
  - cron: '30 15 * * *'  # 21:00 IST
```

## Troubleshooting

### Scheduler Not Running at Expected Times

**Check**:
1. Timezone is set correctly: `Asia/Kolkata`
2. System time is accurate
3. Scheduler is running (check logs)

**Fix**:
```bash
# Restart scheduler
python phase6/scheduler.py
```

### Too Many/Few Reports

**Adjust interval**:
```bash
# More frequent (every 2 hours)
python phase6/scheduler.py --interval 120

# Less frequent (every 6 hours)
python phase6/scheduler.py --interval 360
```

### GitHub Actions Not Running

**Check**:
1. Workflow is enabled in GitHub
2. Secrets are configured (GROQ_API_KEY)
3. Cron syntax is correct

**Test manually**:
1. Go to Actions tab in GitHub
2. Select "Scheduled Pulse Report Generation"
3. Click "Run workflow"

## Files Modified

1. **`phase6/scheduler.py`**
   - Changed default interval from 5 to 180 minutes
   - Updated log messages to show hours
   - Added run times display

2. **`start-scheduler.bat`**
   - Updated schedule display
   - Added run times information

3. **`.github/workflows/scheduled-pulse-report.yml`**
   - Changed cron from `*/5 * * * *` to `0 */3 * * *`
   - Updated comments

4. **`SCHEDULER_UPDATE_180MIN.md`**
   - This documentation

## Next Steps

1. **Restart the scheduler** to apply changes:
   ```bash
   start-scheduler.bat
   ```

2. **Verify the schedule** in logs:
   ```bash
   Get-Content phase6/logs/scheduler.log | Select-Object -Last 20
   ```

3. **Wait for next run** (check "Next run" time in logs)

4. **Monitor emails** at manshuc12@gmail.com

5. **Adjust if needed** using `--interval` parameter

---

## Summary

✅ Scheduler updated to run every 180 minutes (3 hours)
✅ 8 reports per day at predictable times
✅ More efficient resource usage
✅ Better data quality with more accumulated reviews
✅ Reduced email fatigue

The scheduler is now configured for a professional, sustainable cadence! 🎯
