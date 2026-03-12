"""Phase 4: Report Generation - Generate weekly pulse report from themes."""
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phase4.report_generator import ReportGenerator
from common.models import Theme, Review
from common.config import Config


def load_phase3_output(filepath: str) -> tuple[list[Theme], dict]:
    """Load theme analysis output from Phase 3.
    
    Args:
        filepath: Path to Phase 3 output JSON file
    
    Returns:
        Tuple of (themes list, metadata dict)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Parse themes
    themes = []
    for theme_data in data['themes']:
        # Parse sample reviews (Phase 3 only stores samples, not all reviews)
        reviews = []
        for review_data in theme_data['sample_reviews']:
            review = Review(
                review_id=review_data['review_id'],
                rating=review_data['rating'],
                text=review_data['text'],
                date=datetime.fromisoformat(review_data.get('date', datetime.now().isoformat())),
                is_sanitized=True,
                language='en'
            )
            reviews.append(review)
        
        # Create Theme object
        # Note: We use sample reviews for quote selection, but keep the actual frequency count
        theme = Theme(
            label=theme_data['label'],
            description=theme_data['description'],
            reviews=reviews,
            frequency=len(reviews),  # Use sample count for validation
            rank=theme_data['rank']
        )
        # Store the actual frequency as an attribute for reporting
        theme.actual_frequency = theme_data['frequency']
        themes.append(theme)
    
    return themes, data['metadata']


def main():
    """Run Phase 4: Report Generation."""
    print("=" * 80)
    print("PHASE 4: REPORT GENERATION")
    print("=" * 80)
    print()
    
    # Step 1: Load Phase 3 output
    print("Step 1: Loading Phase 3 theme analysis output...")
    phase3_output_dir = Path(__file__).parent / "phase3" / "output"
    
    # Find the most recent Phase 3 output file
    phase3_files = sorted(phase3_output_dir.glob("phase3_output_*.json"), reverse=True)
    if not phase3_files:
        # Try parent directory structure
        phase3_output_dir = Path(__file__).parent.parent / "phase3" / "phase3" / "output"
        phase3_files = sorted(phase3_output_dir.glob("phase3_output_*.json"), reverse=True)
    
    if not phase3_files:
        print("ERROR: No Phase 3 output files found!")
        print(f"Searched in: {phase3_output_dir}")
        return
    
    phase3_file = phase3_files[0]
    print(f"Loading: {phase3_file}")
    
    themes, phase3_metadata = load_phase3_output(str(phase3_file))
    print(f"✓ Loaded {len(themes)} themes")
    print(f"  Total reviews: {phase3_metadata['total_reviews']}")
    print()
    
    # Step 2: Initialize Report Generator
    print("Step 2: Initializing Report Generator...")
    try:
        generator = ReportGenerator()
        print(f"✓ Using Groq model: {generator.model}")
        print()
    except ValueError as e:
        print(f"ERROR: {e}")
        print("Make sure GROQ_API_KEY is set in .env file")
        return
    
    # Step 3: Generate report
    print("Step 3: Generating weekly pulse report...")
    print("  - Selecting top 3 themes")
    print("  - Selecting 3 representative quotes")
    print("  - Generating 3 action ideas using Groq LLM...")
    
    try:
        # Use date range from Phase 3 metadata
        date_range_str = phase3_metadata.get('date_range', ['2026-02-19', '2026-03-12'])
        from datetime import date
        date_range = (
            date.fromisoformat(date_range_str[0]) if isinstance(date_range_str, list) else date(2026, 2, 19),
            date.fromisoformat(date_range_str[1]) if isinstance(date_range_str, list) else date(2026, 3, 12)
        )
        
        report, metadata = generator.generate_report(
            themes=themes,
            date_range=date_range,
            total_review_count=phase3_metadata['total_reviews']
        )
        
        print(f"✓ Report generated successfully!")
        print(f"  Word count: {report.word_count} / {Config.REPORT_WORD_LIMIT}")
        print(f"  Themes: {len(report.themes)}")
        print(f"  Quotes: {len(report.quotes)}")
        print(f"  Action ideas: {len(report.action_ideas)}")
        print()
        
    except Exception as e:
        print(f"ERROR: Failed to generate report: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Format and display report
    print("Step 4: Formatting report...")
    formatted_report = generator.format_report(report)
    print()
    print(formatted_report)
    print()
    
    # Step 5: Save output
    print("Step 5: Saving output...")
    output_dir = Path(__file__).parent / "phase4" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"phase4_output_{timestamp}.json"
    
    # Prepare output data
    output_data = {
        "metadata": {
            "generation_timestamp": metadata.timestamp.isoformat(),
            "word_count": metadata.word_count,
            "model_version": metadata.model_version,
            "date_range": [str(report.date_range[0]), str(report.date_range[1])],
            "review_count": report.review_count
        },
        "report": {
            "themes": [
                {
                    "rank": theme.rank,
                    "label": theme.label,
                    "description": theme.description,
                    "frequency": getattr(theme, 'actual_frequency', theme.frequency)
                }
                for theme in report.themes
            ],
            "quotes": report.quotes,
            "action_ideas": report.action_ideas,
            "word_count": report.word_count
        },
        "formatted_report": formatted_report
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Output saved to: {output_file}")
    print()
    
    # Step 6: Summary
    print("=" * 80)
    print("PHASE 4 COMPLETE")
    print("=" * 80)
    print(f"✓ Generated pulse report with {report.word_count} words")
    print(f"✓ Top 3 themes identified:")
    for i, theme in enumerate(report.themes, 1):
        freq = getattr(theme, 'actual_frequency', theme.frequency)
        print(f"  {i}. {theme.label} ({freq} reviews)")
    print(f"✓ 3 user quotes selected")
    print(f"✓ 3 action ideas generated")
    print()
    print("Next: Run Phase 5 to draft email with this report")
    print("=" * 80)


if __name__ == "__main__":
    main()
