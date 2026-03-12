"""Test script for email sending functionality."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from email_drafter import EmailDrafter
from common.models import PulseReport, Theme, Review
from datetime import datetime, date

def test_email_sending():
    """Test email sending with a sample report."""
    
    print("=" * 60)
    print("EMAIL SENDING TEST")
    print("=" * 60)
    print()
    
    # Create sample reviews for theme 1
    reviews1 = [
        Review(
            rating=5,
            text="Great app for investing. Very easy to use and understand.",
            date=datetime.now(),
            review_id="test_1",
            is_sanitized=True,
            language="en"
        ),
        Review(
            rating=5,
            text="Simple interface makes investing accessible.",
            date=datetime.now(),
            review_id="test_2",
            is_sanitized=True,
            language="en"
        )
    ]
    
    # Create sample reviews for theme 2
    reviews2 = [
        Review(
            rating=2,
            text="Too many technical issues. App crashes frequently.",
            date=datetime.now(),
            review_id="test_3",
            is_sanitized=True,
            language="en"
        )
    ]
    
    # Create sample reviews for theme 3
    reviews3 = [
        Review(
            rating=4,
            text="Good features but needs better customer support.",
            date=datetime.now(),
            review_id="test_4",
            is_sanitized=True,
            language="en"
        )
    ]
    
    # Create 3 sample themes (required by PulseReport)
    theme1 = Theme(
        label="Ease of Use",
        description="Users appreciate the simple and intuitive interface",
        reviews=reviews1,
        frequency=2,
        rank=1
    )
    
    theme2 = Theme(
        label="Technical Issues",
        description="Users report app crashes and stability problems",
        reviews=reviews2,
        frequency=1,
        rank=2
    )
    
    theme3 = Theme(
        label="Customer Support",
        description="Users request better support and response times",
        reviews=reviews3,
        frequency=1,
        rank=3
    )
    
    # Create test report with 3 themes
    report = PulseReport(
        date_range=(date(2026, 3, 6), date(2026, 3, 13)),
        themes=[theme1, theme2, theme3],
        quotes=[
            "Great app for investing. Very easy to use and understand.",
            "Too many technical issues. App crashes frequently.",
            "Good features but needs better customer support."
        ],
        action_ideas=[
            "Maintain the simple UI while adding advanced features",
            "Prioritize fixing critical bugs causing app crashes",
            "Improve customer support response times and channels"
        ],
        word_count=75,
        review_count=100,
        generation_timestamp=datetime.now()
    )
    
    # Get recipient email
    recipient = input("Enter recipient email address (or press Enter for manshuc12@gmail.com): ").strip()
    if not recipient:
        recipient = "manshuc12@gmail.com"
    
    print()
    print(f"Recipient: {recipient}")
    print()
    
    # Confirm
    confirm = input("Send test email? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Test cancelled.")
        return
    
    print()
    print("Sending test email...")
    print()
    
    try:
        # Create drafter with email sending enabled
        drafter = EmailDrafter(send_email=True)
        
        # Draft and send email
        content, metadata = drafter.draft_email(
            report=report,
            recipient=recipient
        )
        
        print("=" * 60)
        print("RESULT")
        print("=" * 60)
        print(f"Email sent: {metadata.email_sent}")
        print(f"Draft saved: {metadata.output_path}")
        print(f"Recipient: {metadata.recipient}")
        print(f"Timestamp: {metadata.timestamp}")
        print("=" * 60)
        
        if metadata.email_sent:
            print()
            print("✅ SUCCESS! Email sent successfully.")
            print(f"Check inbox: {recipient}")
            print("(Also check spam folder)")
        else:
            print()
            print("❌ FAILED! Email was not sent.")
            print("Check the error messages above.")
            print("Review EMAIL_SETUP_GUIDE.md for troubleshooting.")
        
    except Exception as e:
        print("=" * 60)
        print("ERROR")
        print("=" * 60)
        print(f"❌ {str(e)}")
        print()
        print("Troubleshooting:")
        print("1. Check your .env file has SMTP settings")
        print("2. Verify SMTP_USERNAME and SMTP_PASSWORD are correct")
        print("3. Make sure you're using an App Password (not regular password)")
        print("4. Review EMAIL_SETUP_GUIDE.md for setup instructions")
        print("=" * 60)


if __name__ == '__main__':
    test_email_sending()
