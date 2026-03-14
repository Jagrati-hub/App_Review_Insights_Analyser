"""Email Drafter for formatting and sending pulse reports via email."""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.models import PulseReport, DraftMetadata
from common.config import Config
from phase5.email_template_inline import generate_html_email

logger = logging.getLogger(__name__)


class EmailDrafter:
    """Drafts and sends emails containing weekly pulse reports."""
    
    def __init__(self, output_dir: Optional[str] = None, send_email: bool = True):
        """Initialize email drafter.
        
        Args:
            output_dir: Directory to save email drafts (defaults to phase5/drafts/)
            send_email: Whether to send emails via SMTP (default: True)
        """
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path(__file__).parent / "drafts"
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Email sending configuration
        self.send_email = send_email
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.smtp_username = Config.SMTP_USERNAME
        self.smtp_password = Config.SMTP_PASSWORD
        self.sender_email = Config.SENDER_EMAIL
        self.sender_name = Config.SENDER_NAME
    
    def draft_email(
        self,
        report: PulseReport,
        recipient: str,
        sender_name: Optional[str] = None
    ) -> tuple[str, DraftMetadata]:
        """Draft and optionally send an email containing the pulse report.
        
        Args:
            report: PulseReport object to format as email
            recipient: Email address of recipient
            sender_name: Name of sender (defaults to Config.SENDER_NAME)
        
        Returns:
            Tuple of (email_content, DraftMetadata)
        """
        # Validate recipient email
        if not recipient or '@' not in recipient:
            raise ValueError(f"Invalid recipient email: {recipient}")
        
        # Use configured sender name if not provided
        if sender_name is None:
            sender_name = self.sender_name
        
        # Format subject line with date range
        subject = self._format_subject(report)
        
        # Format plain text body (for draft)
        text_body = self._format_body(report, sender_name)
        email_content = self._format_email(subject, recipient, text_body)
        
        # Save plain text draft
        output_path = self._save_draft(email_content, report)
        
        # Format HTML body (for email only)
        html_body = self._format_html_body(report, sender_name)
        
        # Send email if enabled (HTML only)
        email_sent = False
        error_message = None
        if self.send_email:
            try:
                self._send_email_html_only(recipient, subject, html_body)
                email_sent = True
                logger.info(f"✅ Email sent successfully to {recipient}")
            except Exception as e:
                error_message = str(e)
                logger.error(f"❌ Failed to send email to {recipient}: {error_message}")
                # Continue even if email fails - draft is still saved
        
        # Create metadata
        metadata = DraftMetadata(
            recipient=recipient,
            timestamp=datetime.now(),
            output_path=str(output_path),
            email_sent=email_sent,
            error_message=error_message
        )
        
        return email_content, metadata
    
    def _format_subject(self, report: PulseReport) -> str:
        """Format email subject line with date range.
        
        Args:
            report: PulseReport object
        
        Returns:
            Subject line string
        """
        start_date = report.date_range[0].strftime("%b %d")
        end_date = report.date_range[1].strftime("%b %d, %Y")
        
        return f"Play Store Pulse Report - Week of {start_date} to {end_date}"
    
    def _format_body(self, report: PulseReport, sender_name: str) -> str:
        """Format email body with report content.
        
        Args:
            report: PulseReport object
            sender_name: Name of sender
        
        Returns:
            Email body string
        """
        lines = []
        
        # Greeting
        lines.append("Hi Team,")
        lines.append("")
        
        # Add statistics
        stats_line = f"Here's your weekly pulse report based on {report.review_count} Google Play Store reviews"
        if report.average_rating:
            stats_line += f" (Avg Rating: {report.average_rating}⭐)"
        stats_line += f" from {report.date_range[0].strftime('%B %d')} to {report.date_range[1].strftime('%B %d, %Y')}."
        lines.append(stats_line)
        
        if report.positive_count is not None and report.negative_count is not None:
            lines.append(f"Positive Reviews (4-5★): {report.positive_count} | Negative Reviews (1-3★): {report.negative_count}")
        lines.append("")
        
        # Top Themes Section
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("📊 TOP THEMES")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        
        for i, theme in enumerate(report.themes, 1):
            freq = getattr(theme, 'actual_frequency', theme.frequency)
            avg_rating = theme.average_rating if theme.average_rating else 0.0
            stars = '⭐' * int(round(avg_rating))
            lines.append(f"{i}. {theme.label} ({freq} reviews • {stars} {avg_rating:.1f})")
            lines.append(f"   {theme.description}")
            lines.append("")
        
        # User Voices Section
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("💬 USER VOICES")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        
        for i, quote in enumerate(report.quotes, 1):
            lines.append(f"{i}. \"{quote}\"")
            lines.append("")
        
        # Action Ideas Section
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("💡 ACTION ROADMAP")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        
        for i, idea in enumerate(report.action_ideas, 1):
            lines.append(f"{i}. {idea}")
            lines.append("")
        
        # Footer
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        lines.append("Best regards,")
        lines.append(sender_name)
        lines.append("")
        lines.append(f"Report generated: {report.generation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Word count: {report.word_count}")
        
        return "\n".join(lines)
    
    def _format_email(self, subject: str, recipient: str, body: str) -> str:
        """Format complete email with headers and body.
        
        Args:
            subject: Email subject line
            recipient: Recipient email address
            body: Email body content
        
        Returns:
            Complete email string
        """
        lines = []
        lines.append(f"To: {recipient}")
        lines.append(f"Subject: {subject}")
        lines.append("")
        lines.append(body)
        
        return "\n".join(lines)
    
    def _save_draft(self, email_content: str, report: PulseReport) -> Path:
        """Save email draft to file as plain text.
        
        Args:
            email_content: Complete plain text email content
            report: PulseReport object (for timestamp)
        
        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"email_draft_{timestamp}.txt"
        output_path = self.output_dir / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(email_content)
        except Exception as e:
            raise IOError(f"Failed to save email draft: {e}")
        
        return output_path
    
    def preview_email(self, email_content: str) -> None:
        """Print email preview to console.
        
        Args:
            email_content: Complete email content
        """
        print("\n" + "=" * 80)
        print("EMAIL DRAFT PREVIEW")
        print("=" * 80)
        print(email_content)
        print("=" * 80 + "\n")
    
    def _format_html_body(self, report: PulseReport, sender_name: str) -> str:
        """Format email body as HTML with inline styles for email client compatibility.
        
        Args:
            report: PulseReport object
            sender_name: Name of sender
        
        Returns:
            HTML email body string with inline styles
        """
        start_date = report.date_range[0].strftime("%B %d")
        end_date = report.date_range[1].strftime("%B %d, %Y")
        
        return generate_html_email(report, sender_name, start_date, end_date)
    
    def _send_email_html_only(self, recipient: str, subject: str, html_body: str) -> None:
        """Send email via SMTP with HTML only (no plain text fallback).
        
        Args:
            recipient: Recipient email address
            subject: Email subject line
            html_body: HTML email body
        
        Raises:
            Exception: If email sending fails
        """
        # Validate SMTP configuration
        if not self.smtp_username or not self.smtp_password:
            raise ValueError("SMTP credentials not configured. Set SMTP_USERNAME and SMTP_PASSWORD in .env")
        
        if not self.sender_email:
            raise ValueError("Sender email not configured. Set SENDER_EMAIL in .env")
        
        try:
            # Create HTML-only message
            message = MIMEText(html_body, 'html', 'utf-8')
            message['From'] = f"{self.sender_name} <{self.sender_email}>"
            message['To'] = recipient
            message['Subject'] = subject
            message['Content-Type'] = 'text/html; charset=utf-8'
            
            # Connect to SMTP server
            logger.info(f"Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
            
            if self.smtp_port == 465:
                # Use SSL
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30)
            else:
                # Use TLS
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
                server.starttls()
            
            # Login
            logger.info(f"Logging in as: {self.smtp_username}")
            server.login(self.smtp_username, self.smtp_password)
            
            # Send email
            logger.info(f"Sending HTML-only email to: {recipient}")
            server.send_message(message)
            
            # Close connection
            server.quit()
            
            logger.info(f"HTML email sent successfully to {recipient}")
            
        except smtplib.SMTPAuthenticationError as e:
            raise Exception(f"SMTP authentication failed. Check your email and password: {str(e)}")
        except smtplib.SMTPException as e:
            raise Exception(f"SMTP error occurred: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to send email: {str(e)}")
