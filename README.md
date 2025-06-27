# realtime_newsletter

Financial Newsletter Bot
An automated newsletter generator that fetches financial news from NewsAPI, categorizes articles by sector, and creates a formatted HTML newsletter.

#Quick Start

Install dependencies:

bashpip install requests spacy jinja2
python -m spacy download en_core_web_sm

Get NewsAPI key: Sign up at newsapi.org and replace the API key in the code
Create template: Add a newsletter_template.html file in the same directory
Run:

bashpython main.py

#Features

Multi-sector Coverage: Technology, Pharmaceuticals, Energy, Automotive, Finance, Real Estate, Retail
Smart Categorization: Uses spaCy NLP to categorize articles by keywords
Auto Summarization: Generates concise summaries for each article
HTML Output: Creates formatted newsletter with automatic browser opening
Sector Grouping: Organizes articles by industry for easy reading

#Configuration
Sectors: Modify the SECTORS dictionary to add/remove industries and keywords
Query: Customize the NewsAPI search query in get_newsapi_articles() call
Output: Articles are automatically saved as financial_newsletter_YYYY-MM-DD.html

#Required Files

main.py - Main application
newsletter_template.html - HTML template (create this)

#Security Note
Replace the hardcoded API key with an environment variable for production use.
