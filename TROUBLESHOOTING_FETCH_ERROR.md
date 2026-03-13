# Troubleshooting "Failed to Fetch" Error

## Issue Fixed ✅
Updated `google-play-scraper` from version 1.2.4 to 1.2.7

## Current Status
- ✅ Backend running on http://localhost:5000
- ✅ Frontend running on http://localhost:3000
- ✅ Scraper library updated
- ✅ Test script confirms scraper works

## If Error Persists

### 1. Refresh Your Browser
- Hard refresh: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
- Clear browser cache
- Try in incognito/private mode

### 2. Check Network Connection
The error `getaddrinfo failed` indicates DNS/network issues:

**Test connection:**
```bash
python test_scraper_connection.py
```

If this fails, try:
- Restart your router/modem
- Switch to a different network (mobile hotspot)
- Use a VPN
- Check Windows Firewall settings

### 3. Firewall/Antivirus
Some security software blocks the Play Store scraper:
- Temporarily disable Windows Firewall
- Temporarily disable antivirus
- Add Python to firewall exceptions

### 4. DNS Issues
Try changing DNS servers:
- Google DNS: 8.8.8.8, 8.8.4.4
- Cloudflare DNS: 1.1.1.1, 1.0.0.1

### 5. Proxy Settings
If you're behind a corporate proxy:
```python
# Add to phase1/review_scraper.py if needed
import os
os.environ['HTTP_PROXY'] = 'http://your-proxy:port'
os.environ['HTTPS_PROXY'] = 'http://your-proxy:port'
```

### 6. Rate Limiting
Google Play Store may temporarily block requests:
- Wait 5-10 minutes
- Try with fewer weeks (8 instead of 12)
- Reduce batch size in config

## Testing Steps

1. **Test scraper directly:**
   ```bash
   python test_scraper_connection.py
   ```

2. **Test backend health:**
   ```bash
   curl http://localhost:5000/api/health
   ```

3. **Check backend logs:**
   Look for error messages in the backend terminal

4. **Try generating report:**
   - Go to http://localhost:3000
   - Select 8 weeks (smaller dataset)
   - Enter your email
   - Click "Generate Report"

## Common Error Messages

### "getaddrinfo failed"
- **Cause**: DNS resolution failure
- **Fix**: Check internet connection, try different DNS

### "Connection timeout"
- **Cause**: Network/firewall blocking
- **Fix**: Check firewall, try VPN

### "Too many requests"
- **Cause**: Rate limiting by Google
- **Fix**: Wait 10 minutes, try again

## Success Indicators

When working correctly, you should see:
1. Frontend shows "Scraping reviews..." progress
2. Backend logs show "Fetched X reviews"
3. Process completes in 3-7 minutes
4. Email sent successfully

## Still Having Issues?

1. Check all services are running:
   ```bash
   # Backend should show: Running on http://localhost:5000
   # Frontend should show: Ready in X.Xs
   ```

2. Restart all services:
   - Stop backend (Ctrl+C in backend terminal)
   - Stop frontend (Ctrl+C in frontend terminal)
   - Run: `start-all.bat`

3. Check logs:
   - Backend terminal for Python errors
   - Frontend terminal for React errors
   - Browser console (F12) for JavaScript errors

## Contact Information
If issues persist, check:
- Google Play Scraper GitHub: https://github.com/JoMingyu/google-play-scraper
- Project documentation in SETUP_GUIDE.md
