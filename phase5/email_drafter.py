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
        
        # Format HTML body (for email)
        html_body = self._format_html_body(report, sender_name)
        
        # For draft file, create a simple text version
        plain_body = self._format_body(report, sender_name)
        email_content = self._format_email(subject, recipient, plain_body)
        
        # Save to file
        output_path = self._save_draft(email_content, report)
        
        # Send email if enabled (HTML only)
        email_sent = False
        if self.send_email:
            try:
                self._send_email_html_only(recipient, subject, html_body)
                email_sent = True
                logger.info(f"✅ Email sent successfully to {recipient}")
            except Exception as e:
                logger.error(f"❌ Failed to send email to {recipient}: {str(e)}")
                # Continue even if email fails - draft is still saved
        
        # Create metadata
        metadata = DraftMetadata(
            recipient=recipient,
            timestamp=datetime.now(),
            output_path=str(output_path),
            email_sent=email_sent
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
        lines.append(f"Here's your weekly pulse report based on {report.review_count} Google Play Store reviews from {report.date_range[0].strftime('%B %d')} to {report.date_range[1].strftime('%B %d, %Y')}.")
        lines.append("")
        
        # Top Themes Section
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("📊 TOP THEMES")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        
        for i, theme in enumerate(report.themes, 1):
            freq = getattr(theme, 'actual_frequency', theme.frequency)
            lines.append(f"{i}. {theme.label} ({freq} reviews)")
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
        lines.append("💡 ACTION IDEAS")
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
        """Save email draft to file.
        
        Args:
            email_content: Complete email content
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
        """Format email body as HTML with attractive styling.
        
        Args:
            report: PulseReport object
            sender_name: Name of sender
        
        Returns:
            HTML email body string
        """
        start_date = report.date_range[0].strftime("%B %d")
        end_date = report.date_range[1].strftime("%B %d, %Y")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #1a202c;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px 0;
        }}
        .email-wrapper {{
            max-width: 650px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .header {{
            background: linear-gradient(135deg, #5a67d8 0%, #667eea 50%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        .header::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse 15s ease-in-out infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.1); }}
        }}
        .header-content {{
            position: relative;
            z-index: 1;
        }}
        .header h1 {{
            margin: 0;
            font-size: 32px;
            font-weight: 700;
            letter-spacing: -0.5px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header .emoji {{
            font-size: 48px;
            display: block;
            margin-bottom: 10px;
            animation: bounce 2s ease-in-out infinite;
        }}
        @keyframes bounce {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-10px); }}
        }}
        .header p {{
            margin: 12px 0 0 0;
            font-size: 18px;
            opacity: 0.95;
            font-weight: 500;
        }}
        .stats-bar {{
            background: linear-gradient(to right, #f7fafc 0%, #edf2f7 100%);
            padding: 25px 30px;
            display: flex;
            justify-content: space-around;
            border-bottom: 2px solid #e2e8f0;
            gap: 20px;
        }}
        .stat {{
            text-align: center;
            flex: 1;
            padding: 10px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            transition: transform 0.2s ease;
        }}
        .stat:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .stat-label {{
            font-size: 11px;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            margin-top: 4px;
        }}
        .content {{
            padding: 40px 30px;
            background-color: #ffffff;
        }}
        .greeting {{
            color: #2d3748;
            margin-bottom: 30px;
            font-size: 15px;
            line-height: 1.8;
            padding: 20px;
            background: linear-gradient(to right, #f7fafc 0%, #ffffff 100%);
            border-left: 4px solid #667eea;
            border-radius: 8px;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section-title {{
            font-size: 24px;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            padding-bottom: 12px;
            border-bottom: 3px solid #e2e8f0;
        }}
        .section-title .emoji {{
            font-size: 28px;
            margin-right: 12px;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
        }}
        .theme-card {{
            background: linear-gradient(135deg, #f7fafc 0%, #ffffff 100%);
            border-left: 5px solid #667eea;
            padding: 20px;
            margin-bottom: 16px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        .theme-card::before {{
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 100px;
            height: 100%;
            background: linear-gradient(90deg, transparent 0%, rgba(102,126,234,0.05) 100%);
        }}
        .theme-card:hover {{
            transform: translateX(4px);
            box-shadow: 0 6px 20px rgba(102,126,234,0.15);
        }}
        .theme-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            position: relative;
            z-index: 1;
        }}
        .theme-title {{
            font-size: 18px;
            font-weight: 700;
            color: #1a202c;
            flex: 1;
        }}
        .theme-badge {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 700;
            box-shadow: 0 2px 8px rgba(102,126,234,0.3);
            white-space: nowrap;
        }}
        .theme-description {{
            font-size: 15px;
            color: #4a5568;
            line-height: 1.7;
            position: relative;
            z-index: 1;
        }}
        .quote-card {{
            background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
            border-left: 5px solid #fc8181;
            padding: 20px 24px;
            margin-bottom: 16px;
            border-radius: 12px;
            font-style: italic;
            color: #2d3748;
            box-shadow: 0 4px 12px rgba(252,129,129,0.1);
            position: relative;
            transition: all 0.3s ease;
        }}
        .quote-card::before {{
            content: '"';
            position: absolute;
            top: 10px;
            left: 10px;
            font-size: 60px;
            color: rgba(252,129,129,0.15);
            font-family: Georgia, serif;
            line-height: 1;
        }}
        .quote-card:hover {{
            transform: translateX(4px);
            box-shadow: 0 6px 20px rgba(252,129,129,0.2);
        }}
        .quote-text {{
            position: relative;
            z-index: 1;
            font-size: 15px;
            line-height: 1.7;
        }}
        .action-item {{
            background: linear-gradient(135deg, #f0fff4 0%, #ffffff 100%);
            border-left: 5px solid #48bb78;
            padding: 20px;
            margin-bottom: 16px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(72,187,120,0.1);
            display: flex;
            align-items: flex-start;
            transition: all 0.3s ease;
        }}
        .action-item:hover {{
            transform: translateX(4px);
            box-shadow: 0 6px 20px rgba(72,187,120,0.2);
        }}
        .action-number {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            min-width: 32px;
            height: 32px;
            border-radius: 50%;
            font-weight: 700;
            font-size: 16px;
            margin-right: 16px;
            box-shadow: 0 2px 8px rgba(72,187,120,0.3);
            flex-shrink: 0;
        }}
        .action-text {{
            flex: 1;
            font-size: 15px;
            color: #2d3748;
            line-height: 1.7;
        }}
        .footer {{
            background: linear-gradient(to bottom, #f7fafc 0%, #edf2f7 100%);
            padding: 30px;
            text-align: center;
            border-top: 2px solid #e2e8f0;
        }}
        .footer p {{
            margin: 8px 0;
            font-size: 14px;
            color: #4a5568;
        }}
        .footer strong {{
            color: #2d3748;
            font-weight: 600;
        }}
        .divider {{
            height: 2px;
            background: linear-gradient(to right, transparent 0%, #cbd5e0 50%, transparent 100%);
            margin: 20px 0;
        }}
        .footer-meta {{
            color: #718096;
            font-size: 12px;
            margin-top: 15px;
        }}
        .footer-brand {{
            color: #a0aec0;
            font-size: 11px;
            margin-top: 10px;
            font-weight: 500;
        }}
        .logo {{
            display: inline-block;
            width: 8px;
            height: 8px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            margin: 0 4px;
        }}
    </style>
</head>
<body>
    <div class="email-wrapper">
        <!-- Header -->
        <div class="header">
            <div class="header-content">
                <span class="emoji">📊</span>
                <h1>Play Store Pulse Report</h1>
                <p>Week of {start_date} to {end_date}</p>
            </div>
        </div>
        
        <!-- Stats Bar -->
        <div class="stats-bar">
            <div class="stat">
                <div class="stat-value">{report.review_count}</div>
                <div class="stat-label">Reviews</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(report.themes)}</div>
                <div class="stat-label">Themes</div>
            </div>
            <div class="stat">
                <div class="stat-value">{report.word_count}</div>
                <div class="stat-label">Words</div>
            </div>
        </div>
        
        <!-- Content -->
        <div class="content">
            <div class="greeting">
                <strong>Hi Team,</strong><br><br>
                Here's your weekly pulse report based on <strong>{report.review_count}</strong> Google Play Store reviews 
                from <strong>{start_date}</strong> to <strong>{end_date}</strong>.
            </div>
            
            <!-- Top Themes Section -->
            <div class="section">
                <div class="section-title">
                    <span class="emoji">📊</span>
                    <span>Top Themes</span>
                </div>
"""
        
        # Add themes
        for i, theme in enumerate(report.themes, 1):
            freq = getattr(theme, 'actual_frequency', theme.frequency)
            html += f"""
                <div class="theme-card">
                    <div class="theme-header">
                        <div class="theme-title">{i}. {theme.label}</div>
                        <div class="theme-badge">{freq} reviews</div>
                    </div>
                    <div class="theme-description">{theme.description}</div>
                </div>
"""
        
        html += """
            </div>
            
            <!-- User Voices Section -->
            <div class="section">
                <div class="section-title">
                    <span class="emoji">💬</span>
                    <span>User Voices</span>
                </div>
"""
        
        # Add quotes
        for quote in report.quotes:
            html += f"""
                <div class="quote-card">
                    <div class="quote-text">{quote}</div>
                </div>
"""
        
        html += """
            </div>
            
            <!-- Action Ideas Section -->
            <div class="section">
                <div class="section-title">
                    <span class="emoji">💡</span>
                    <span>Action Ideas</span>
                </div>
"""
        
        # Add action ideas
        for i, idea in enumerate(report.action_ideas, 1):
            html += f"""
                <div class="action-item">
                    <span class="action-number">{i}</span>
                    <span class="action-text">{idea}</span>
                </div>
"""
        
        html += f"""
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p><strong>Best regards,</strong></p>
            <p><strong>{sender_name}</strong></p>
            <div class="divider"></div>
            <p class="footer-meta">Report generated: {report.generation_timestamp.strftime('%B %d, %Y at %H:%M:%S')}</p>
            <p class="footer-brand">
                <span class="logo"></span>
                Powered by Groq LLM
                <span class="logo"></span>
                Groww Product Team
                <span class="logo"></span>
            </p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
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
            # Create message with HTML only
            message = MIMEMultipart()
            message['From'] = f"{self.sender_name} <{self.sender_email}>"
            message['To'] = recipient
            message['Subject'] = subject
            
            # Attach HTML version only
            html_part = MIMEText(html_body, 'html', 'utf-8')
            message.attach(html_part)
            
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
