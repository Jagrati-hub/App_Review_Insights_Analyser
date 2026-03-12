# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automated pulse report generation.

## Quick Start

### 1. Setup (One-time)

Add your Groq API key as a GitHub secret:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `GROQ_API_KEY`
4. Value: Your Groq API key

### 2. Run Manual Report

1. Go to **Actions** tab
2. Select **Manual Pulse Report Generation**
3. Click **Run workflow**
4. Configure and run

### 3. Enable Scheduled Reports

The scheduled workflow runs every 5 minutes automatically once enabled.

## Available Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **Scheduled Pulse Report** | Every 5 minutes | Automated report generation |
| **Manual Pulse Report** | On-demand | Custom report generation |
| **Test Pipeline** | Push/PR | Code validation |

## Files

- `workflows/scheduled-pulse-report.yml` - Automated scheduling
- `workflows/manual-pulse-report.yml` - Manual trigger
- `workflows/test-pipeline.yml` - Testing
- `GITHUB_ACTIONS_GUIDE.md` - Complete documentation

## Documentation

See [GITHUB_ACTIONS_GUIDE.md](GITHUB_ACTIONS_GUIDE.md) for:
- Detailed setup instructions
- Usage examples
- Troubleshooting
- Best practices
- Advanced configuration

## Architecture

```
GitHub Actions
     │
     ├─ Scheduled (every 5 min)
     │   └─ Run scheduler.py --test
     │       └─ Generate report
     │           └─ Upload artifacts
     │
     ├─ Manual (on-demand)
     │   └─ Run with custom params
     │       └─ Generate report
     │           └─ Upload artifacts
     │           └─ Commit to repo (optional)
     │
     └─ Test (on push/PR)
         └─ Validate code
             └─ Check syntax
             └─ Verify imports
```

## Quick Links

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Groq Console](https://console.groq.com/)
- [Main README](../README.md)
- [Scheduler Guide](../phase6/SCHEDULER_GUIDE.md)
