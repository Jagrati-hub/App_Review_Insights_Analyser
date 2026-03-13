"""Test script to diagnose Play Store scraper connection issues."""
import sys
from google_play_scraper import reviews, Sort

print("Testing Google Play Store connection...")
print("=" * 60)

try:
    print("\n1. Testing basic connection to Play Store...")
    result, token = reviews(
        'com.nextbillion.groww',
        lang='en',
        country='us',
        sort=Sort.NEWEST,
        count=5
    )
    
    print(f"✅ SUCCESS! Retrieved {len(result)} reviews")
    print(f"   First review rating: {result[0]['score'] if result else 'N/A'}")
    print(f"   Connection is working properly!")
    
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}")
    print(f"   Message: {str(e)}")
    print("\nPossible solutions:")
    print("1. Check if you're behind a corporate firewall/proxy")
    print("2. Try using a VPN")
    print("3. Check if google-play-scraper needs updating: pip install --upgrade google-play-scraper")
    print("4. Try a different network connection")
    sys.exit(1)

print("\n" + "=" * 60)
print("All tests passed! The scraper is working correctly.")
