# GitHub Actions Integration Guide

This guide explains how to use GitHub Actions for automated pulse report generation.

## Overview

Three GitHub Actions workflows are available:

1. **Scheduled Pulse Report** - Runs automatically every 5 minutes
2. **Manual Pulse Report** - Trigger on-demand with custom parameters
3. **Test Pipeline** - Validates code on push/PR

## Setup Instructions

### 1. Add GitHub Secrets

You need to add your Groq API key as a GitHub secret:

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secret:
   - **Name**: `GROQ_API_KEY`
   - **Value**: Your Groq API key from https://console.groq.com/

### 2. Enable GitHub Actions

1. Go to **Actions** tab in your repository
2. If prompted, click **I understand my workflows, go ahead and enable them**
3. You should see three workflows listed

### 3. Configure Scheduled Workflow (Optional)

The scheduled workflow runs every 5 minutes by default. To change the schedule:

1. Edit `.github/workflows/scheduled-pulse-report.yml`
2. Modify the cron expression:
   ```yaml
   schedule:
     - cron: '*/5 * * * *'  # Every 5 minutes
   ```

**Common cron patterns:**
- `*/5 * * * *` - Every 5 minutes
- `0 * * * *` - Every hour
- `0 13 * * *` - Daily at 1:00 PM UTC
- `0 13 * * 1` - Weekly on Monday at 1:00 PM UTC

**Note**: GitHub Actions uses UTC timezone. IST = UTC + 5:30

## Workflows

### 1. Scheduled Pulse Report

**File**: `.github/workflows/scheduled-pulse-report.yml`

**Trigger**: Automatically every 5 minutes (or custom schedule)

**What it does:**
1. Sets up Python environment
2. Installs dependencies
3. Runs pulse report generation
4. Uploads reports as artifacts
5. Optionally commits reports to repository

**Configuration:**
- Recipient: `manshuc12@gmail.com` (hardcoded)
- Weeks back: `10` (default)
- Schedule: Every 5 minutes

**Artifacts:**
- Reports saved for 30 days
- Accessible from Actions → Workflow run → Artifacts

### 2. Manual Pulse Report

**File**: `.github/workflows/manual-pulse-report.yml`

**Trigger**: Manual (workflow_dispatch)

**How to run:**
1. Go to **Actions** tab
2. Select **Manual Pulse Report Generation**
3. Click **Run workflow**
4. Configure parameters:
   - **Weeks back**: 8-12 (dropdown)
   - **Recipient email**: Email address
   - **Commit results**: true/false
5. Click **Run workflow**

**What it does:**
1. Generates report with custom parameters
2. Uploads artifacts (90-day retention)
3. Optionally commits to repository
4. Creates summary in workflow run

**Use cases:**
- Test report generation
- Generate reports for different time periods
- Generate reports for different recipients

### 3. Test Pipeline

**File**: `.github/workflows/test-pipeline.yml`

**Trigger**: 
- Push to main/develop branches
- Pull requests to main/develop
- Manual trigger

**What it does:**
1. Checks Python syntax
2. Verifies imports
3. Tests configuration
4. Runs unit tests (if available)

**Use cases:**
- Validate code changes
- Ensure dependencies are correct
- Catch errors before deployment

## Usage Examples

### Example 1: View Scheduled Reports

1. Go to **Actions** tab
2. Click on **Scheduled Pulse Report Generation**
3. Click on a recent workflow run
4. Scroll to **Artifacts** section
5. Download `pulse-report-XXX.zip`
6. Extract to view JSON reports and email drafts

### Example 2: Generate Custom Report

1. Go to **Actions** tab
2. Click **Manual Pulse Report Generation**
3. Click **Run workflow**
4. Set parameters:
   - Weeks back: `12`
   - Recipient: `team@example.com`
   - Commit results: `true`
5. Click **Run workflow**
6. Wait for completion (~5-10 minutes)
7. Download artifacts or view committed files

### Example 3: Test Before Deployment

1. Create a new branch
2. Make code changes
3. Push to GitHub
4. **Test Pipeline** runs automatically
5. Check results in Actions tab
6. Fix any errors before merging

## Artifact Management

### Accessing Artifacts

**Via GitHub UI:**
1. Actions → Workflow run → Artifacts
2. Click artifact name to download

**Via GitHub CLI:**
```bash
# List artifacts
gh run list --workflow=scheduled-pulse-report.yml

# Download latest artifact
gh run download --name pulse-report-XXX
```

### Artifact Contents

Each artifact contains:
- `phase6/reports/weekly_pulse_*.json` - Report data
- `phase6/reports/email_draft_*.txt` - Email draft
- `phase6/logs/scheduler.log` - Execution logs

### Retention Periods

- **Scheduled reports**: 30 days
- **Manual reports**: 90 days
- **Test artifacts**: Default (90 days)

## Monitoring

### View Workflow Status

**Dashboard:**
- Go to **Actions** tab
- See all workflow runs with status indicators
- Green ✓ = Success
- Red ✗ = Failure
- Yellow ● = In progress

**Email Notifications:**
- GitHub sends emails on workflow failures
- Configure in Settings → Notifications

### Check Logs

1. Go to workflow run
2. Click on job name (e.g., "generate-report")
3. Expand steps to view logs
4. Download logs if needed

### Troubleshooting

**Common Issues:**

1. **Missing GROQ_API_KEY**
   - Error: "Groq API key is required"
   - Solution: Add secret in repository settings

2. **Rate Limiting**
   - Error: "API rate limit exceeded"
   - Solution: Reduce schedule frequency or upgrade Groq plan

3. **Workflow Not Running**
   - Check if Actions are enabled
   - Verify cron syntax
   - Check workflow file syntax

4. **Import Errors**
   - Run Test Pipeline to identify issues
   - Check requirements.txt
   - Verify Python version compatibility

## Cost Considerations

### GitHub Actions

- **Free tier**: 2,000 minutes/month for private repos
- **Public repos**: Unlimited minutes
- **Cost**: ~$0.008/minute for private repos (after free tier)

**Estimated usage:**
- Each run: ~5-10 minutes
- Every 5 minutes: ~288 runs/day
- Monthly: ~8,640 runs = 43,200-86,400 minutes

**Recommendation**: Use scheduled workflow sparingly or upgrade to GitHub Pro/Team

### Groq API

- Check Groq pricing at https://console.groq.com/
- Monitor usage in Groq dashboard
- Set up usage alerts

## Best Practices

### 1. Schedule Optimization

**For production:**
```yaml
# Weekly on Monday at 1 PM UTC (6:30 PM IST)
schedule:
  - cron: '0 13 * * 1'
```

**For testing:**
```yaml
# Every 5 minutes (use sparingly)
schedule:
  - cron: '*/5 * * * *'
```

### 2. Artifact Management

- Download and archive important reports locally
- Clean up old artifacts periodically
- Use longer retention for critical reports

### 3. Error Handling

- Monitor workflow failures
- Set up Slack/email notifications
- Review logs regularly

### 4. Security

- Never commit API keys to repository
- Use GitHub secrets for sensitive data
- Restrict workflow permissions if needed

### 5. Testing

- Test workflows manually before enabling schedule
- Use Test Pipeline on all code changes
- Validate reports before relying on automation

## Advanced Configuration

### Custom Workflow

Create a custom workflow for specific needs:

```yaml
name: Custom Report

on:
  schedule:
    - cron: '0 9 * * 1'  # Weekly Monday 9 AM UTC
  workflow_dispatch:

jobs:
  custom-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python phase6/scheduler.py --test --weeks 8
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
```

### Notifications

Add Slack notifications:

```yaml
- name: Notify Slack
  if: always()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "Pulse report: ${{ job.status }}"
      }
```

### Matrix Builds

Generate reports for multiple configurations:

```yaml
strategy:
  matrix:
    weeks: [8, 10, 12]
steps:
  - run: python phase6/scheduler.py --test --weeks ${{ matrix.weeks }}
```

## Migration from Local Scheduler

To migrate from local scheduler to GitHub Actions:

1. **Disable local scheduler**: Stop `start-scheduler.bat`
2. **Set up GitHub Actions**: Follow setup instructions above
3. **Test manually**: Run Manual Pulse Report workflow
4. **Enable schedule**: Uncomment schedule in workflow file
5. **Monitor**: Check first few runs for issues

## Support

For issues:
1. Check workflow logs in Actions tab
2. Review this guide
3. Check GitHub Actions documentation
4. Review Groq API status

## Summary

GitHub Actions provides:
- ✅ Automated report generation
- ✅ No local infrastructure needed
- ✅ Artifact storage and management
- ✅ Flexible scheduling
- ✅ Manual trigger capability
- ✅ Built-in monitoring and logging

Perfect for:
- Production deployments
- Team collaboration
- Reliable automation
- Scalable infrastructure
