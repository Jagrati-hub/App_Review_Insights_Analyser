"""Phase 5: Email Drafting - Draft email with pulse report."""
import json
import sys
import os
from datetime import datetime, date
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phase5.email_drafter import EmailDrafter
from common.models import PulseReport, Theme, Review


def load_phase4_output(filepath: str) -> PulseReport:
    """Load pulse report from Phase 4 output.
    
    Args:
        filepath: Path to Phase 4 output JSON file
    
    Returns:
        PulseReport object
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    report_data = data['report']
    metadata = data['metadata']
    
    # Parse themes (simplified - no reviews needed for email)
    themes = []
    for theme_data in report_data['themes']:
        # Create a dummy review to satisfy validation
        dummy_review = Review(
            review_id="dummy",
            rating=5,
            text="dummy",
            date=datetime.now(),
            is_sanitized=True
        )
        
        theme = Theme(
            label=theme_data['label'],
            description=theme_data['description'],
            reviews=[dummy_review],  # Single dummy review for validation
            frequency=1,  # Matches review count for validation
            rank=theme_data['rank']
        )
        # Store actual frequency
        theme.actual_frequency = theme_data['frequency']
        themes.append(theme)
    
    # Parse date range
    date_range = (
        date.fromisoformat(metadata['date_range'][0]),
        date.fromisoformat(metadata['date_range'][1])
    )
    
    # Create PulseReport
    report = PulseReport(
        date_range=date_range,
        themes=themes,
        quotes=report_data['quotes'],
        action_ideas=report_data['action_ideas'],
        word_count=report_data['word_count'],
        review_count=metadata['review_count'],
        generation_timestamp=datetime.fromisoformat(metadata['generation_timestamp'])
    )
    
    return report


def main():
    """Run Phase 5: Email Drafting."""
    print("=" * 80)
    print("PHASE 5: EMAIL DRAFTING")
    print("=" * 80)
    print()
    
    # Step 1: Load Phase 4 output
    print("Step 1: Loading Phase 4 pulse report output...")
    phase4_output_dir = Path(__file__).parent / "phase4" / "output"
    
    # Find the most recent Phase 4 output file
    phase4_files = sorted(phase4_output_dir.glob("phase4_output_*.json"), reverse=True)
    if not phase4_files:
        # Try parent directory structure
        phase4_output_dir = Path(__file__).parent.parent / "phase4" / "phase4" / "output"
        phase4_files = sorted(phase4_output_dir.glob("phase4_output_*.json"), reverse=True)
    
    if not phase4_files:
        print("ERROR: No Phase 4 output files found!")
        print(f"Searched in: {phase4_output_dir}")
        return
    
    phase4_file = phase4_files[0]
    print(f"Loading: {phase4_file}")
    
    report = load_phase4_output(str(phase4_file))
    print(f"✓ Loaded pulse report")
    print(f"  Date range: {report.date_range[0]} to {report.date_range[1]}")
    print(f"  Review count: {report.review_count}")
    print(f"  Word count: {report.word_count}")
    print()
    
    # Step 2: Get recipient email
    print("Step 2: Setting recipient email...")
    # For demo purposes, use a placeholder email
    # In production, this would come from UI input or config
    recipient_email = os.getenv('RECIPIENT_EMAIL', 'team@example.com')
    print(f"Recipient: {recipient_email}")
    print()
    
    # Step 3: Initialize Email Drafter
    print("Step 3: Initializing Email Drafter...")
    drafter = EmailDrafter()
    print(f"✓ Email drafts will be saved to: {drafter.output_dir}")
    print()
    
    # Step 4: Draft email
    print("Step 4: Drafting email...")
    try:
        email_content, metadata = drafter.draft_email(
            report=report,
            recipient=recipient_email,
            sender_name="Groww Product Team"
        )
        
        print(f"✓ Email drafted successfully!")
        print(f"  Recipient: {metadata.recipient}")
        print(f"  Saved to: {metadata.output_path}")
        print()
        
    except Exception as e:
        print(f"ERROR: Failed to draft email: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 5: Preview email
    print("Step 5: Email preview...")
    drafter.preview_email(email_content)
    
    # Step 6: Save metadata
    print("Step 6: Saving metadata...")
    output_dir = Path(__file__).parent / "phase5" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    metadata_file = output_dir / f"phase5_metadata_{timestamp}.json"
    
    metadata_data = {
        "recipient": metadata.recipient,
        "timestamp": metadata.timestamp.isoformat(),
        "output_path": metadata.output_path,
        "report_summary": {
            "date_range": [str(report.date_range[0]), str(report.date_range[1])],
            "review_count": report.review_count,
            "word_count": report.word_count,
            "themes_count": len(report.themes),
            "quotes_count": len(report.quotes),
            "action_ideas_count": len(report.action_ideas)
        }
    }
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Metadata saved to: {metadata_file}")
    print()
    
    # Step 7: Summary
    print("=" * 80)
    print("PHASE 5 COMPLETE")
    print("=" * 80)
    print(f"✓ Email draft created and saved")
    print(f"✓ Recipient: {recipient_email}")
    print(f"✓ Draft location: {metadata.output_path}")
    print()
    print("Email contains:")
    print(f"  • {len(report.themes)} top themes")
    print(f"  • {len(report.quotes)} user quotes")
    print(f"  • {len(report.action_ideas)} action ideas")
    print(f"  • {report.word_count} words total")
    print()
    print("Next: Implement Flask UI (Phase 2) to trigger the full pipeline")
    print("=" * 80)


if __name__ == "__main__":
    main()
