# Implementation Plan: Play Store Review Analyzer

## Overview

This implementation follows a 6-phase approach building a web-based system that scrapes Google Play Store reviews for the Groww app and generates weekly pulse reports. The system uses Flask for the web interface, google-play-scraper for fetching reviews, and Groq LLM for theme analysis and report generation. Phase 1 has been updated to scale to 5,000 reviews with a length filter (minimum 5 words) and removal of the title field from output.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create Python project with virtual environment
  - Install core dependencies: Flask, Flask-WTF, google-play-scraper, hypothesis (for testing)
  - Create directory structure: `app/`, `tests/`, `templates/`, `static/`
  - Set up configuration management for API keys and app settings
  - _Requirements: 6.1, 7.1_

- [-] 2. Implement core data models
  - [x] 2.1 Create data model classes in `models.py`
    - Implement Review, Theme, PulseReport dataclasses
    - Implement supporting models: ScrapingSummary, PIISummary, AnalysisMetadata, GenerationMetadata
    - Implement configuration models: GroqConfig, ScraperConfig, SystemConfig
    - Implement UI models: AnalysisRequest, PipelineStatus, ReportView
    - Add validation in `__post_init__` methods
    - _Requirements: 1.6, 2.3, 3.1, 3.2, 3.3, 3.4, 7.2, 7.3_
  
  - [ ]* 2.2 Write unit tests for data models
    - Test Review validation (rating range, required fields)
    - Test Theme validation (frequency matching review count)
    - Test PulseReport validation (3 themes, 3 quotes, 3 actions, word limit)
    - Test AnalysisRequest validation (weeks_back range, email format)
    - Test PipelineStatus validation (valid status values, progress range)
    - _Requirements: 1.6, 3.4, 7.2, 7.3_

- [x] 3. Implement Review_Scraper with google-play-scraper (Phase 1 - Updated)
  - [x] 3.1 Create Review_Scraper class in `review_scraper.py`
    - Implement `scrape_reviews()` method with google-play-scraper integration
    - Configure to fetch 5,000 reviews (not 200) from Groww app (com.nextbillion.groww)
    - Implement date range filtering (8-12 weeks back)
    - Add length filter: Discard reviews with fewer than 5 words
    - Remove title field from Review objects (only keep review body and metadata)
    - Implement batch fetching with 1-second delays between batches
    - Add retry logic with exponential backoff (3 attempts)
    - Validate rating is 1-5 stars, skip invalid reviews with warnings
    - Return list of Review objects and ScrapingSummary
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_
  
  - [ ]* 3.2 Write unit tests for Review_Scraper
    - Test scraping with mocked google-play-scraper responses
    - Test date range filtering (10 weeks back)
    - Test length filter (reviews with <5 words are discarded)
    - Test title field is not included in output
    - Test handling of missing content field (skip with warning)
    - Test handling of invalid rating (skip with warning)
    - Test Play Store unavailable error handling
    - Test network timeout with retry logic
    - Test rate limiting with delays between batches
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_
  
  - [ ]* 3.3 Write property tests for Review_Scraper
    - **Property 1: Valid App ID and Scraping Success**
    - **Validates: Requirements 1.1**
    - **Property 2: Complete Field Extraction**
    - **Validates: Requirements 1.2, 1.6**
    - **Property 3: Date Range Filtering**
    - **Validates: Requirements 1.3, 1.4**
    - **Property 4: Invalid Review Handling**
    - **Validates: Requirements 1.5**
    - **Property 27: Scraping Retry Logic**
    - **Validates: Requirements 1.7**
    - **Property 28: Scraping Rate Limiting**
    - **Validates: Requirements 1.1**

- [x] 4. Implement PII_Filter (Phase 1)
  - [x] 4.1 Create PII_Filter class in `pii_filter.py`
    - Implement `filter_reviews()` method to process list of reviews
    - Implement `sanitize_text()` method with regex patterns for PII detection
    - Add patterns for: usernames (@username), emails, phone numbers (US and international), user IDs (UUIDs)
    - Replace detected PII with placeholders: [USERNAME], [EMAIL], [PHONE], [USER_ID]
    - Return sanitized reviews and PIISummary with detection counts
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.7_
  
  - [ ]* 4.2 Write unit tests for PII_Filter
    - Test email removal and replacement
    - Test phone number removal (US format: +1-XXX-XXX-XXXX)
    - Test phone number removal (international format: +XX-XXX-XXX-XXXX)
    - Test username removal (@username pattern)
    - Test UUID pattern removal
    - Test text with no PII (should remain unchanged)
    - Test text with multiple PII types
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.7_
  
  - [ ]* 4.3 Write property tests for PII_Filter
    - **Property 13: Comprehensive PII Removal**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**
    - **Property 15: PII Placeholder Replacement**
    - **Validates: Requirements 4.7**

- [x] 5. Checkpoint - Ensure Phase 1 tests pass
  - Run all unit tests for Review_Scraper and PII_Filter
  - Run property tests with 100 iterations minimum
  - Verify scraper can fetch 5,000 reviews with length filter
  - Verify title field is not in output
  - Ensure all tests pass, ask the user if questions arise

- [x] 6. Implement UI_Controller with Flask (Phase 2)
  - [x] 6.1 Create Flask application in `ui_controller.py`
    - Initialize Flask app with configuration
    - Set up Flask-WTF for form handling
    - Create AnalysisConfigForm with weeks_back (8-12) and recipient_email fields
    - Add form validators: NumberRange for weeks_back, Email for recipient_email
    - Implement route handlers: GET `/` (index), POST `/analyze`, GET `/status`
    - _Requirements: 7.1, 7.2, 7.3, 7.6_
  
  - [x] 6.2 Create HTML templates
    - Create `templates/index.html` with configuration form
    - Create `templates/report.html` for displaying pulse reports
    - Create `templates/error.html` for error messages
    - Add basic CSS styling in `static/style.css`
    - _Requirements: 7.1, 7.4, 7.7_
  
  - [x] 6.3 Implement pipeline orchestration in UI_Controller
    - Add `run_pipeline()` method to execute full analysis workflow
    - Implement pipeline status tracking with PipelineStatus model
    - Add error handling for scraping failures, API errors
    - Display progress updates during pipeline execution
    - _Requirements: 7.6, 7.7_
  
  - [ ]* 6.4 Write unit tests for UI_Controller
    - Test index page renders with form
    - Test form validation with valid inputs (weeks_back=10, valid email)
    - Test form validation rejects invalid weeks_back (7, 13)
    - Test form validation rejects invalid email format
    - Test POST to /analyze endpoint triggers pipeline
    - Test GET to /status endpoint returns pipeline status
    - Test error page displays when scraping fails
    - _Requirements: 7.1, 7.2, 7.3, 7.6, 7.7, 7.8_
  
  - [ ]* 6.5 Write property tests for UI_Controller
    - **Property 24: UI Form Validation for Date Range**
    - **Validates: Requirements 7.2, 7.8**
    - **Property 25: UI Email Format Validation**
    - **Validates: Requirements 7.3**
    - **Property 26: Pipeline Status Tracking**
    - **Validates: Requirements 7.6**

- [ ] 7. Checkpoint - Ensure Phase 2 tests pass
  - Run all unit tests for UI_Controller
  - Run property tests with 100 iterations minimum
  - Verify UI loads and displays configuration form
  - Verify form validation works correctly
  - Ensure all tests pass, ask the user if questions arise

- [x] 8. Implement Groq LLM integration (Phase 3)
  - [x] 8.1 Create Groq API client in `groq_client.py`
    - Implement API wrapper with authentication (API key)
    - Add retry logic with exponential backoff for API errors
    - Implement timeout handling (30 seconds default)
    - Add rate limiting handling (429 errors)
    - Log model version for reproducibility
    - _Requirements: 6.1, 6.2, 6.5, 6.6_
  
  - [x] 8.2 Create Theme_Analyzer class in `theme_analyzer.py`
    - Implement `analyze_themes()` method using Groq LLM
    - Create prompt template for theme identification (max 5 themes)
    - Parse JSON response from LLM into Theme objects
    - Rank themes by frequency (most common first)
    - Ensure each review is assigned to at least one theme
    - Handle API errors with retry guidance
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 6.1, 6.2, 6.3, 6.5_
  
  - [ ]* 8.3 Write unit tests for Theme_Analyzer
    - Test theme analysis with mocked Groq API responses
    - Test handling of 10 reviews with clear themes
    - Test handling of single review
    - Test API authentication failure
    - Test API timeout with retry logic
    - Test malformed API response handling
    - Test model version is included in logs
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.6, 6.1, 6.2, 6.5, 6.6_
  
  - [ ]* 8.4 Write property tests for Theme_Analyzer
    - **Property 5: Theme Count Constraint**
    - **Validates: Requirements 2.2, 2.5**
    - **Property 6: Theme Labeling**
    - **Validates: Requirements 2.3**
    - **Property 7: Theme Frequency Ranking**
    - **Validates: Requirements 2.4**
    - **Property 8: Complete Review Assignment**
    - **Validates: Requirements 2.6**
    - **Property 20: API Error Handling**
    - **Validates: Requirements 6.2, 6.5**
    - **Property 21: Model Version Logging**
    - **Validates: Requirements 6.6**

- [ ] 9. Checkpoint - Ensure Phase 3 tests pass
  - Run all unit tests for Groq integration and Theme_Analyzer
  - Run property tests with 100 iterations minimum
  - Verify successful Groq API calls for theme analysis
  - Verify error handling with retries works correctly
  - Ensure all tests pass, ask the user if questions arise

- [x] 10. Implement Report_Generator (Phase 4)
  - [x] 10.1 Create Report_Generator class in `report_generator.py`
    - Implement `generate_report()` method to create PulseReport
    - Select top 3 themes by frequency
    - Implement quote selection algorithm (3 quotes from different themes)
    - Use Groq LLM to generate 3 action ideas based on themes
    - Create prompt template for action idea generation
    - Validate word count does not exceed 250 words
    - Format report with sections: TOP THEMES, USER VOICES, ACTION IDEAS
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 6.4_
  
  - [ ]* 10.2 Write unit tests for Report_Generator
    - Test report generation from 3 themes
    - Test report generation from 2 themes (edge case)
    - Test quote selection from different themes
    - Test action idea generation with mocked Groq API
    - Test word count calculation and validation
    - Test report structure has all required sections
    - Test handling of action idea generation failure
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_
  
  - [ ]* 10.3 Write property tests for Report_Generator
    - **Property 9: Top Themes Selection**
    - **Validates: Requirements 3.1**
    - **Property 10: Report Structure Constraints**
    - **Validates: Requirements 3.2, 3.3**
    - **Property 11: Word Count Limit**
    - **Validates: Requirements 3.4**
    - **Property 12: Quote Theme Diversity**
    - **Validates: Requirements 3.6**
    - **Property 14: PII-Free Report Output**
    - **Validates: Requirements 4.6**
    - **Property 20: API Error Handling**
    - **Validates: Requirements 6.2, 6.5**

- [ ] 11. Checkpoint - Ensure Phase 4 tests pass
  - Run all unit tests for Report_Generator
  - Run property tests with 100 iterations minimum
  - Verify reports meet all constraints (3 themes, 3 quotes, 3 actions, ≤250 words)
  - Verify action ideas are relevant and actionable
  - Ensure all tests pass, ask the user if questions arise

- [-] 12. Implement Email_Drafter and complete UI integration (Phase 5)
  - [x] 12.1 Create Email_Drafter class in `email_drafter.py`
    - Implement `draft_email()` method to format PulseReport as email
    - Create email template with subject line: "Play Store Pulse Report - Week of {start_date} to {end_date}"
    - Structure email body with sections for themes, quotes, and action ideas
    - Include recipient address as configurable parameter
    - Write email draft to file (text format)
    - Return file path and DraftMetadata
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ] 12.2 Complete UI integration for report display
    - Update `templates/report.html` to display PulseReport content
    - Add email draft preview section
    - Add "Send Email" button (displays draft, does not actually send)
    - Update pipeline status tracking to show progress through all phases
    - Add error display for each pipeline stage
    - _Requirements: 7.4, 7.6, 7.7_
  
  - [ ]* 12.3 Write unit tests for Email_Drafter
    - Test email draft creation with standard report
    - Test subject line format includes date range
    - Test recipient address appears in output
    - Test email body contains all required sections (themes, quotes, actions)
    - Test file write and verify file exists
    - Test handling of file write failure
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 12.4 Write property tests for Email_Drafter
    - **Property 16: Email Subject Date Range**
    - **Validates: Requirements 5.2**
    - **Property 17: Email Structure Completeness**
    - **Validates: Requirements 5.3**
    - **Property 18: Email Recipient Configuration**
    - **Validates: Requirements 5.4**
    - **Property 19: Email File Output**
    - **Validates: Requirements 5.5**
  
  - [ ]* 12.5 Write integration tests for end-to-end pipeline
    - Test full pipeline: UI form → Scrape → Filter → Analyze → Generate → Draft → Display
    - Verify no PII in final email draft
    - Verify report meets all constraints
    - Verify email draft is displayed correctly in UI
    - Verify status updates during pipeline execution
    - Test error handling at each pipeline stage
    - _Requirements: 1.1, 2.1, 3.1, 4.6, 5.1, 7.1, 7.6_

- [ ] 13. Checkpoint - Ensure Phase 5 tests pass
  - Run all unit tests for Email_Drafter and UI integration
  - Run property tests with 100 iterations minimum
  - Run integration tests for full pipeline
  - Verify end-to-end workflow from UI to email draft
  - Ensure all tests pass, ask the user if questions arise

- [ ] 14. Complete testing and documentation (Phase 6)
  - [ ] 14.1 Run extended property tests
    - Run all property tests with 1000 iterations (extended validation)
    - Verify all 28 properties pass consistently
    - Document any edge cases discovered
    - _Requirements: All_
  
  - [ ] 14.2 Verify test coverage
    - Run coverage report (target: 80%+ coverage)
    - Add tests for any uncovered code paths
    - Ensure all error handling paths are tested
    - _Requirements: All_
  
  - [ ] 14.3 Create user documentation
    - Write README with setup instructions
    - Document configuration parameters (API keys, app settings)
    - Create user guide for web interface
    - Document API integration (Groq LLM)
    - Add troubleshooting section
    - _Requirements: 6.1, 7.1, 7.2, 7.3_
  
  - [ ] 14.4 Create deployment guide
    - Document Flask app deployment steps
    - Add environment variable configuration
    - Create requirements.txt with all dependencies
    - Add Docker configuration (optional)
    - Document security considerations (API key management)
    - _Requirements: 6.1, 7.1_
  
  - [ ]* 14.5 Performance testing and optimization
    - Test with 5,000 reviews (Phase 1 scale)
    - Test with reviews containing extensive PII
    - Test with very long review text (5000+ characters)
    - Verify end-to-end pipeline completes in <60 seconds
    - Optimize any bottlenecks discovered
    - _Requirements: 1.1, 4.1_

- [ ] 15. Final checkpoint - System ready for production
  - All 28 properties validated with 1000 iterations
  - Test coverage meets 80%+ target
  - Documentation is complete and clear
  - Performance meets benchmarks
  - Flask app can be deployed
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Phase 1 has been updated: 5,000 reviews (not 200), length filter (min 5 words), no title field in output
- Property tests require hypothesis library and minimum 100 iterations per test
- Integration tests should use mocked API responses to avoid actual API calls during testing
- The system uses Python with Flask for web interface and google-play-scraper for review fetching
- Groq LLM (mixtral-8x7b-32768 model) is used for theme analysis and action idea generation
