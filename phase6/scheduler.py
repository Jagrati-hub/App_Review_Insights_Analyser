"""Automated scheduler for weekly pulse report generation."""
import os
import sys
import time
import logging
from datetime import datetime, timedelta
from typing import Optional
import schedule
import pytz

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.models import AnalysisRequest
from phase2.pipeline_orchestrator import PipelineOrchestrator

# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configure logging to separate file
log_file = os.path.join(log_dir, 'scheduler.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WeeklyPulseScheduler:
    """Scheduler for automated weekly pulse report generation."""
    
    def __init__(
        self,
        recipient_email: str = "manshuc12@gmail.com",
        schedule_interval: int = 180,  # Run every 180 minutes (3 hours)
        timezone: str = "Asia/Kolkata",  # IST
        weeks_back: int = 10
    ):
        """Initialize the scheduler.
        
        Args:
            recipient_email: Email address to send reports to
            schedule_interval: Interval in minutes (default: 180 = 3 hours)
            timezone: Timezone for scheduling (default: Asia/Kolkata for IST)
            weeks_back: Number of weeks of reviews to analyze
        """
        self.recipient_email = recipient_email
        self.schedule_interval = schedule_interval
        self.timezone = pytz.timezone(timezone)
        self.weeks_back = weeks_back
        self.orchestrator = PipelineOrchestrator()
        
        logger.info(f"Scheduler initialized:")
        logger.info(f"  - Recipient: {self.recipient_email}")
        logger.info(f"  - Schedule: Every {self.schedule_interval} minutes ({self.schedule_interval // 60} hours)")
        logger.info(f"  - Timezone: {timezone}")
        logger.info(f"  - Analysis window: {self.weeks_back} weeks")
        logger.info(f"  - Log file: {log_file}")
    
    def generate_weekly_pulse(self):
        """Generate and send weekly pulse report."""
        try:
            logger.info("=" * 60)
            logger.info("Starting scheduled pulse generation")
            logger.info("=" * 60)
            
            # Generate unique request ID
            timestamp = datetime.now()
            request_id = f"req_{timestamp.strftime('%Y%m%d_%H%M%S')}_{timestamp.microsecond}"
            
            # Create analysis request
            request = AnalysisRequest(
                weeks_back=self.weeks_back,
                recipient_email=self.recipient_email,
                request_timestamp=timestamp,
                request_id=request_id
            )
            
            logger.info(f"Request ID: {request.request_id}")
            logger.info(f"Analyzing reviews from past {self.weeks_back} weeks")
            logger.info(f"Recipient: {self.recipient_email}")
            
            # Run pipeline
            logger.info("Starting pipeline execution...")
            result = self.orchestrator.run_pipeline(request)
            
            logger.info(f"Pipeline execution completed with status: {result.get('status')}")
            
            if result.get('status') == 'complete':
                logger.info("✅ Pulse generated successfully!")
                logger.info(f"Report ID: {request.request_id}")
                
                # Log summary
                metadata = result.get('metadata', {})
                scraping = metadata.get('scraping', {})
                logger.info(f"Reviews analyzed: {scraping.get('valid_reviews', 0)}")
                logger.info(f"Date range: {scraping.get('date_range', [])}")
                
                # Save report to file
                self._save_report(request.request_id, result)
                
            elif result.get('status') == 'error':
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"❌ Pulse generation failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"❌ Scheduler error: {str(e)}", exc_info=True)
        
        finally:
            logger.info("=" * 60)
            logger.info(f"Next run scheduled for: {self._get_next_run_time()}")
            logger.info("=" * 60)
    
    def _save_report(self, request_id: str, result: dict):
        """Save generated report to file.
        
        Args:
            request_id: Unique request identifier
            result: Pipeline result dictionary
        """
        try:
            import json
            from pathlib import Path
            
            # Create output directory
            output_dir = Path("phase6/reports")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = output_dir / f"weekly_pulse_{timestamp}.json"
            
            # Save report
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Report saved to: {report_file}")
            
            # Also save email draft separately
            email_draft = result.get('email_draft', '')
            if email_draft:
                email_file = output_dir / f"email_draft_{timestamp}.txt"
                with open(email_file, 'w', encoding='utf-8') as f:
                    f.write(email_draft)
                logger.info(f"Email draft saved to: {email_file}")
                
        except Exception as e:
            logger.error(f"Failed to save report: {str(e)}")
    
    def _get_next_run_time(self) -> str:
        """Get the next scheduled run time.
        
        Returns:
            Formatted string of next run time
        """
        try:
            next_run = schedule.next_run()
            if next_run:
                # Convert to IST
                next_run_ist = next_run.astimezone(self.timezone)
                return next_run_ist.strftime("%Y-%m-%d %H:%M:%S %Z")
            return "Not scheduled"
        except Exception:
            return "Unknown"
    
    def start(self):
        """Start the scheduler (blocking)."""
        logger.info("=" * 60)
        logger.info("PULSE SCHEDULER STARTED")
        logger.info("=" * 60)
        logger.info(f"Current time (IST): {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        logger.info(f"Schedule: Every {self.schedule_interval} minutes ({self.schedule_interval // 60} hours)")
        logger.info(f"Recipient: {self.recipient_email}")
        logger.info(f"Run times: 00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00 IST")
        
        # Schedule the job to run every N minutes
        schedule.every(self.schedule_interval).minutes.do(self.generate_weekly_pulse)
        
        logger.info(f"Next run: {self._get_next_run_time()}")
        logger.info("Press Ctrl+C to stop the scheduler")
        logger.info("=" * 60)
        
        # Run scheduler loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            logger.info("\n" + "=" * 60)
            logger.info("Scheduler stopped by user")
            logger.info("=" * 60)
    
    def run_now(self):
        """Run the pulse generation immediately (for testing)."""
        logger.info("Running pulse generation immediately (test mode)")
        self.generate_weekly_pulse()


def main():
    """Main entry point for scheduler."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Pulse Report Scheduler')
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run immediately for testing (don\'t wait for schedule)'
    )
    parser.add_argument(
        '--email',
        type=str,
        default='manshuc12@gmail.com',
        help='Recipient email address'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=180,
        help='Schedule interval in minutes (default: 180 = 3 hours)'
    )
    parser.add_argument(
        '--weeks',
        type=int,
        default=10,
        help='Number of weeks to analyze'
    )
    
    args = parser.parse_args()
    
    # Create scheduler
    scheduler = WeeklyPulseScheduler(
        recipient_email=args.email,
        schedule_interval=args.interval,
        weeks_back=args.weeks
    )
    
    if args.test:
        # Run immediately for testing
        scheduler.run_now()
    else:
        # Start scheduled execution
        scheduler.start()


if __name__ == '__main__':
    main()
