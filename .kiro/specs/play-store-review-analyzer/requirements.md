# Requirements Document

## Introduction

The Play Store Review Analyzer is a system that fetches and processes recent Google Play Store reviews for the Groww app and generates weekly pulse reports for product teams, support teams, and leadership. The system uses the google-play-scraper library to fetch reviews from the last 8-12 weeks, identifies recurring themes using Groq LLM, and produces a concise one-page report with actionable insights while ensuring no personally identifiable information (PII) is included in any output. A web-based user interface allows users to trigger analysis, configure parameters, view generated reports, and send email drafts.

## Glossary

- **UI_Controller**: Component that provides the web-based user interface for triggering analysis and viewing reports
- **Review_Scraper**: Component responsible for fetching review data directly from Google Play Store using google-play-scraper library
- **Theme_Analyzer**: Component that uses Groq LLM to identify and group reviews into themes
- **Report_Generator**: Component that creates the weekly one-page pulse report
- **Email_Drafter**: Component that formats the report into an email draft
- **PII_Filter**: Component that removes personally identifiable information from all outputs
- **Review**: A Play Store review containing rating, title, text, and date
- **Theme**: A category representing a common topic across multiple reviews
- **Pulse_Report**: The weekly one-page summary document containing themes, quotes, and action ideas
- **Groq_LLM**: The Groq language model API used for analysis
- **Groww_App**: The target Android application (com.nextbillion.groww) from which reviews are fetched

## Requirements

### Requirement 1: Scrape Play Store Reviews

**User Story:** As a product manager, I want to fetch recent Play Store reviews directly from the Groww app, so that I can analyze user feedback from the past 8-12 weeks without manual export.

#### Acceptance Criteria

1. THE Review_Scraper SHALL use google-play-scraper library to fetch reviews from Groww_App (com.nextbillion.groww)
2. WHEN a date range is provided, THE Review_Scraper SHALL fetch reviews within that date range
3. THE Review_Scraper SHALL fetch reviews from the last 8 weeks as the minimum time range
4. THE Review_Scraper SHALL fetch reviews from the last 12 weeks as the maximum time range
5. WHEN a review is missing required fields, THE Review_Scraper SHALL log a warning and skip that review
6. THE Review_Scraper SHALL validate that each review contains a rating between 1 and 5 stars
7. WHEN the Play Store is unavailable, THE Review_Scraper SHALL return an error message with retry guidance

### Requirement 2: Identify Review Themes

**User Story:** As a product manager, I want reviews grouped into themes, so that I can understand common user concerns.

#### Acceptance Criteria

1. WHEN reviews are imported, THE Theme_Analyzer SHALL send review data to Groq_LLM for theme identification
2. THE Theme_Analyzer SHALL group reviews into a maximum of 5 themes
3. THE Theme_Analyzer SHALL assign each theme a descriptive label
4. THE Theme_Analyzer SHALL rank themes by frequency of occurrence across reviews
5. WHEN fewer than 5 distinct themes exist, THE Theme_Analyzer SHALL return only the identified themes
6. THE Theme_Analyzer SHALL associate each review with at least one theme

### Requirement 3: Generate Weekly Pulse Report

**User Story:** As a product manager, I want a one-page weekly report, so that I can quickly understand user sentiment and priorities.

#### Acceptance Criteria

1. THE Report_Generator SHALL create a Pulse_Report containing the top 3 themes by frequency
2. THE Report_Generator SHALL include exactly 3 user quotes in the Pulse_Report
3. THE Report_Generator SHALL include exactly 3 action ideas in the Pulse_Report
4. THE Report_Generator SHALL limit the Pulse_Report to 250 words maximum
5. WHEN generating action ideas, THE Report_Generator SHALL use Groq_LLM to suggest actionable improvements based on themes
6. THE Report_Generator SHALL select user quotes that represent different themes
7. THE Report_Generator SHALL format the Pulse_Report for readability and scanning

### Requirement 4: Remove Personally Identifiable Information

**User Story:** As a compliance officer, I want all PII removed from reports, so that user privacy is protected.

#### Acceptance Criteria

1. THE PII_Filter SHALL remove usernames from all review text before analysis
2. THE PII_Filter SHALL remove email addresses from all review text before analysis
3. THE PII_Filter SHALL remove user IDs from all review text before analysis
4. THE PII_Filter SHALL remove phone numbers from all review text before analysis
5. THE PII_Filter SHALL process all reviews before they are sent to Theme_Analyzer
6. THE PII_Filter SHALL process all content before it is included in the Pulse_Report
7. WHEN PII is detected and removed, THE PII_Filter SHALL replace it with a generic placeholder

### Requirement 5: Draft Email Report

**User Story:** As a product manager, I want an email draft with the pulse report, so that I can easily share insights with my team.

#### Acceptance Criteria

1. WHEN a Pulse_Report is generated, THE Email_Drafter SHALL create an email draft containing the report
2. THE Email_Drafter SHALL format the email with a subject line indicating the week and date range
3. THE Email_Drafter SHALL structure the email body with clear sections for themes, quotes, and action ideas
4. THE Email_Drafter SHALL include the recipient address as a configurable parameter
5. THE Email_Drafter SHALL save the email draft to a file or output format for sending

### Requirement 6: Integrate with Groq LLM

**User Story:** As a developer, I want to use Groq LLM for analysis, so that I can leverage fast and accurate language model capabilities.

#### Acceptance Criteria

1. THE Theme_Analyzer SHALL authenticate with Groq_LLM using an API key
2. WHEN Groq_LLM is unavailable, THE Theme_Analyzer SHALL return an error message with retry guidance
3. THE Theme_Analyzer SHALL send review text to Groq_LLM with a prompt requesting theme identification
4. THE Report_Generator SHALL send theme data to Groq_LLM with a prompt requesting action ideas
5. WHEN Groq_LLM returns an error, THE System SHALL log the error and halt processing
6. THE System SHALL include the Groq_LLM model version in processing logs for reproducibility

### Requirement 7: Provide Web-Based User Interface

**User Story:** As a product manager, I want a web interface to control the analysis process, so that I can easily trigger analysis, configure parameters, and view reports.

#### Acceptance Criteria

1. THE UI_Controller SHALL provide a web page for triggering the review analysis process
2. THE UI_Controller SHALL allow users to configure the date range for review fetching
3. THE UI_Controller SHALL allow users to specify the recipient email address for report delivery
4. WHEN a Pulse_Report is generated, THE UI_Controller SHALL display the report content on the web page
5. THE UI_Controller SHALL provide a button to send the email draft to the configured recipient
6. WHEN the analysis process is running, THE UI_Controller SHALL display progress status to the user
7. WHEN an error occurs during analysis, THE UI_Controller SHALL display the error message to the user
8. THE UI_Controller SHALL validate that the date range is between 8 and 12 weeks before triggering analysis
