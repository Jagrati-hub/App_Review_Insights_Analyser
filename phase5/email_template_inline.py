# Inline-styled HTML email template for maximum email client compatibility

def generate_html_email(report, sender_name, start_date, end_date):
    """Generate HTML email with inline styles for email client compatibility."""
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, Helvetica, sans-serif; background-color: #f4f4f4;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f4f4f4; padding: 20px 0;">
        <tr>
            <td align="center">
                <!-- Main Container -->
                <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; max-width: 600px; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #5a67d8 0%, #667eea 50%, #764ba2 100%); background-color: #667eea; padding: 40px 30px; text-align: center;">
                            <div style="font-size: 48px; margin-bottom: 10px;">📊</div>
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold;">Weekly Pulse Report Of Groww</h1>
                            <p style="margin: 10px 0 0 0; color: #ffffff; font-size: 16px;">Week of {start_date} to {end_date}</p>
                        </td>
                    </tr>
                    
                    <!-- Stats Bar -->
                    <tr>
                        <td style="background-color: #f7fafc; padding: 20px;">
                            <table role="presentation" width="100%" cellpadding="10" cellspacing="0" border="0">
                                <tr>
                                    <td width="25%" align="center" style="background-color: #ffffff; border-radius: 8px; padding: 15px;">
                                        <div style="font-size: 28px; font-weight: bold; color: #667eea; margin-bottom: 5px;">{report.review_count}</div>
                                        <div style="font-size: 10px; color: #718096; text-transform: uppercase; letter-spacing: 0.5px;">Total Reviews</div>
                                    </td>
                                    <td width="25%" align="center" style="background-color: #ffffff; border-radius: 8px; padding: 15px;">
                                        <div style="font-size: 28px; font-weight: bold; color: #667eea; margin-bottom: 5px;">{report.average_rating if report.average_rating else 'N/A'}</div>
                                        <div style="font-size: 10px; color: #718096; text-transform: uppercase; letter-spacing: 0.5px;">Avg Rating</div>
                                    </td>
                                    <td width="25%" align="center" style="background-color: #ffffff; border-radius: 8px; padding: 15px;">
                                        <div style="font-size: 28px; font-weight: bold; color: #48bb78; margin-bottom: 5px;">{report.positive_count if report.positive_count else 0}</div>
                                        <div style="font-size: 10px; color: #718096; text-transform: uppercase; letter-spacing: 0.5px;">Positive (4-5★)</div>
                                    </td>
                                    <td width="25%" align="center" style="background-color: #ffffff; border-radius: 8px; padding: 15px;">
                                        <div style="font-size: 28px; font-weight: bold; color: #fc8181; margin-bottom: 5px;">{report.negative_count if report.negative_count else 0}</div>
                                        <div style="font-size: 10px; color: #718096; text-transform: uppercase; letter-spacing: 0.5px;">Negative (1-3★)</div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 30px;">
                            
                            <!-- Greeting -->
                            <div style="background-color: #f7fafc; border-left: 4px solid #667eea; padding: 20px; margin-bottom: 30px; border-radius: 4px;">
                                <p style="margin: 0; color: #2d3748; font-size: 15px; line-height: 1.6;">
                                    <strong>Hi Team,</strong><br><br>
                                    Here's your weekly pulse report based on <strong>{report.review_count}</strong> Google Play Store reviews 
                                    from <strong>{start_date}</strong> to <strong>{end_date}</strong>.
                                </p>
                            </div>
                            
                            <!-- Top Themes Section -->
                            <h2 style="color: #1a202c; font-size: 22px; margin: 0 0 20px 0; padding-bottom: 10px; border-bottom: 3px solid #e2e8f0;">
                                <span style="font-size: 28px; margin-right: 8px;">📊</span> Top Themes
                            </h2>
"""
    
    # Add themes
    for i, theme in enumerate(report.themes, 1):
        freq = getattr(theme, 'actual_frequency', theme.frequency)
        avg_rating = theme.average_rating if theme.average_rating else 0.0
        stars = '⭐' * int(round(avg_rating))
        
        html += f"""
                            <div style="background-color: #f7fafc; border-left: 5px solid #667eea; padding: 20px; margin-bottom: 15px; border-radius: 4px;">
                                <div style="margin-bottom: 10px;">
                                    <strong style="color: #1a202c; font-size: 17px;">{i}. {theme.label}</strong>
                                    <span style="background-color: #667eea; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; margin-left: 10px; white-space: nowrap;">{freq} reviews • {stars} {avg_rating:.1f}</span>
                                </div>
                                <p style="margin: 0; color: #4a5568; font-size: 14px; line-height: 1.6;">{theme.description}</p>
                            </div>
"""
    
    html += """
                            <!-- User Voices Section -->
                            <h2 style="color: #1a202c; font-size: 22px; margin: 30px 0 20px 0; padding-bottom: 10px; border-bottom: 3px solid #e2e8f0;">
                                <span style="font-size: 28px; margin-right: 8px;">💬</span> User Voices
                            </h2>
"""
    
    # Add quotes
    for quote in report.quotes:
        html += f"""
                            <div style="background-color: #fff5f5; border-left: 5px solid #fc8181; padding: 20px; margin-bottom: 15px; border-radius: 4px; font-style: italic;">
                                <p style="margin: 0; color: #2d3748; font-size: 14px; line-height: 1.6;">"{quote}"</p>
                            </div>
"""
    
    html += """
                            <!-- Action Roadmap Section -->
                            <h2 style="color: #1a202c; font-size: 22px; margin: 30px 0 20px 0; padding-bottom: 10px; border-bottom: 3px solid #e2e8f0;">
                                <span style="font-size: 28px; margin-right: 8px;">💡</span> Action Roadmap
                            </h2>
"""
    
    # Add action ideas
    for i, idea in enumerate(report.action_ideas, 1):
        parts = [p.strip() for p in idea.split('→')]
        title = parts[0] if parts else idea
        steps = parts[1:] if len(parts) > 1 else []
        
        html += f"""
                            <div style="background-color: #ffffff; border: 2px solid #e2e8f0; border-left: 5px solid #48bb78; padding: 20px; margin-bottom: 15px; border-radius: 4px;">
                                <div style="margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #f7fafc;">
                                    <span style="display: inline-block; background-color: #48bb78; color: white; width: 32px; height: 32px; border-radius: 8px; text-align: center; line-height: 32px; font-weight: bold; font-size: 16px; margin-right: 10px;">{i}</span>
                                    <strong style="color: #1a202c; font-size: 16px;">{title}</strong>
                                </div>
"""
        
        if steps and len(steps) >= 2:
            html += """
                                <table role="presentation" width="100%" cellpadding="8" cellspacing="0" border="0">
                                    <tr>
"""
            # First step
            html += f"""
                                        <td width="33%" style="background-color: #e6fffa; border: 2px solid #81e6d9; border-radius: 6px; padding: 10px; text-align: center;">
                                            <div style="font-size: 9px; color: #2c7a7b; text-transform: uppercase; margin-bottom: 4px;">ACTION</div>
                                            <div style="font-size: 13px; color: #2d3748;">{steps[0]}</div>
                                        </td>
"""
            # Middle steps
            for j in range(1, len(steps) - 1):
                html += f"""
                                        <td width="33%" style="background-color: #f7fafc; border: 2px solid #e2e8f0; border-radius: 6px; padding: 10px; text-align: center;">
                                            <div style="font-size: 9px; color: #718096; text-transform: uppercase; margin-bottom: 4px;">STEP {j}</div>
                                            <div style="font-size: 13px; color: #2d3748;">{steps[j]}</div>
                                        </td>
"""
            # Last step
            html += f"""
                                        <td width="33%" style="background-color: #c6f6d5; border: 2px solid #68d391; border-radius: 6px; padding: 10px; text-align: center;">
                                            <div style="font-size: 9px; color: #22543d; text-transform: uppercase; margin-bottom: 4px;">OUTCOME</div>
                                            <div style="font-size: 13px; color: #22543d; font-weight: 600;">{steps[-1]}</div>
                                        </td>
"""
            html += """
                                    </tr>
                                </table>
"""
        elif steps:
            for step in steps:
                html += f"""
                                <div style="padding-left: 42px; color: #4a5568; font-size: 14px; margin-bottom: 6px;">→ {step}</div>
"""
        
        html += """
                            </div>
"""
    
    html += f"""
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f7fafc; padding: 25px; text-align: center; border-top: 2px solid #e2e8f0;">
                            <p style="margin: 0 0 5px 0; color: #4a5568; font-size: 14px;"><strong>Best regards,</strong></p>
                            <p style="margin: 0 0 15px 0; color: #4a5568; font-size: 14px;"><strong>{sender_name}</strong></p>
                            <div style="height: 1px; background-color: #cbd5e0; margin: 15px 0;"></div>
                            <p style="margin: 5px 0; color: #718096; font-size: 12px;">Report generated: {report.generation_timestamp.strftime('%B %d, %Y at %H:%M:%S')}</p>
                            <p style="margin: 5px 0; color: #a0aec0; font-size: 11px;">Powered by Groq LLM • Groww Product Team</p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    return html
