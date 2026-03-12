"""Quick SMTP test script."""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from phase5.email_drafter import EmailDrafter
from common.models import PulseReport, Theme, Review
from datetime import datetime, date

print("=" * 60)
print("SMTP EMAIL TEST")
print("=" * 60)
print()

# Create sample reviews for theme 1
reviews1 = [
    Review(rating=5, text="Great app!", date=datetime.now(), review_id="1", is_sanitized=True, language="en"),
    Review(rating=5, text="Easy to use", date=datetime.now(), review_id="2", is_sanitized=True, language="en")
]

# Create sample reviews for theme 2
reviews2 = [
    Review(rating=2, text="App crashes", date=datetime.now(), review_id="3", is_sanitized=True, language="en")
]

# Create sample reviews for theme 3
reviews3 = [
    Review(rating=4, text="Good support", date=datetime.now(), review_id="4", is_sanitized=True, language="en")
]

# Create 3 themes
theme1 = Theme(label="Ease of Use", description="Simple interface", reviews=reviews1, frequency=2, rank=1)
theme2 = Theme(label="Technical Issues", description="Crashes reported", reviews=reviews2, frequency=1, rank=2)
theme3 = Theme(label="Support", description="Good support", reviews=reviews3, frequency=1, rank=3)

# Create test report
report = PulseReport(
    date_range=(date(2026, 3, 6), date(2026, 3, 13)),
    themes=[theme1, theme2, theme3],
    quotes=["Great app!", "App crashes", "Good support"],
    action_ideas=["Keep UI simple", "Fix crashes", "Improve support"],
    word_count=50,
    review_count=100,
    generation_timestamp=datetime.now()
)

print("Testing email to: manshuc12@gmail.com")
print()

try:
    drafter = EmailDrafter(send_email=True)
    content, metadata = drafter.draft_email(report=report, recipient="manshuc12@gmail.com")
    
    print("=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"✅ Email sent: {metadata.email_sent}")
    print(f"📁 Draft saved: {metadata.output_path}")
    print(f"📧 Recipient: {metadata.recipient}")
    print("=" * 60)
    
    if metadata.email_sent:
        print()
        print("✅ SUCCESS! Check your inbox at manshuc12@gmail.com")
        print("(Also check spam folder)")
    else:
        print()
        print("❌ Email was not sent. Check logs above for errors.")
        
except Exception as e:
    print("=" * 60)
    print("ERROR")
    print("=" * 60)
    print(f"❌ {str(e)}")
    print()
    print("Check:")
    print("1. .env file has correct SMTP_USERNAME and SMTP_PASSWORD")
    print("2. Using Gmail App Password (not regular password)")
    print("3. Review EMAIL_SETUP_GUIDE.md")
    print("=" * 60)
