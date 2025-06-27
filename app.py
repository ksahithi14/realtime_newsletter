import requests
import spacy
from jinja2 import Environment, FileSystemLoader
import datetime
import os # Import the os module for file operations and opening in browser

# --- News API Functions ---
def get_newsapi_articles(api_key, query="finance", language="en", page_size=20):
    """
    Fetches articles from NewsAPI.org based on the given query.

    Args:
        api_key (str): Your NewsAPI.org API key.
        query (str): The search query for articles.
        language (str): The language of the articles (e.g., "en" for English).
        page_size (int): The number of articles to retrieve per request.

    Returns:
        list: A list of dictionaries, each representing an article.
    """
    url = f"https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": language,
        "pageSize": page_size,
        "sortBy": "publishedAt",
        "apiKey": api_key
    }
    response = requests.get(url, params=params)
    response.raise_for_status() # Raise an exception for HTTP errors (e.g., 401, 404, 500)
    data = response.json()
    articles = []
    for article in data['articles']:
        articles.append({
            'title': article.get('title'),
            'link': article.get('url'),
            'published': article.get('publishedAt'),
            'summary': article.get('description'),
            'source': article['source']['name']
        })
    return articles

# --- NLP and Summarization Functions ---
nlp = spacy.load("en_core_web_sm") # Load the spaCy English model once

def categorize_article(article_text, sectors):
    """
    Categorizes an article into relevant sectors based on keywords.

    Args:
        article_text (str): The combined title and summary of the article.
        sectors (dict): A dictionary where keys are sector names and values are lists of keywords.

    Returns:
        list: A list of sector names that the article belongs to.
    """
    doc = nlp(article_text.lower()) # Process text with spaCy for better keyword matching
    article_sectors = []
    for sector, keywords in sectors.items():
        # Check if any keyword for the sector is present in the article text
        if any(keyword in doc.text for keyword in keywords):
            article_sectors.append(sector)
        # More advanced: Could use spaCy's Named Entity Recognition (NER) here
        # to identify organizations and map them to sectors for more robust categorization.
        # Example:
        # for ent in doc.ents:
        #     if ent.label_ == "ORG":
        #         # Lookup entity in a predefined company-to-sector mapping
        #         # e.g., if ent.text == "Microsoft", add "Technology"
        #         pass
    return article_sectors

def summarize_text(text, max_sentences=3):
    """
    Generates a simple extractive summary by taking the first N sentences.

    Args:
        text (str): The input text to summarize.
        max_sentences (int): The maximum number of sentences to include in the summary.

    Returns:
        str: The generated summary.
    """
    doc = nlp(text)
    # Simple summarization: take the first few sentences
    sentences = [sent.text for sent in doc.sents]
    return " ".join(sentences[:max_sentences])

def process_articles(articles, sectors):
    """
    Processes a list of raw articles: categorizes them and generates summaries.

    Args:
        articles (list): A list of raw article dictionaries.
        sectors (dict): The dictionary of sectors and their keywords.

    Returns:
        list: A list of processed article dictionaries, including 'sectors' and 'generated_summary'.
    """
    processed_data = []
    for article in articles:
        # Combine title and summary for comprehensive analysis
        title_and_summary = f"{article.get('title', '')}. {article.get('summary', '')}"
        
        # Categorize the article
        identified_sectors = categorize_article(title_and_summary, sectors)
        
        # Only include articles that are relevant to at least one defined sector
        if identified_sectors:
            article['sectors'] = identified_sectors
            # Generate a summary for the article
            article['generated_summary'] = summarize_text(title_and_summary)
            processed_data.append(article)
    return processed_data

# --- HTML Templating Function ---
# Set up Jinja2 environment to load templates from the current directory
env = Environment(loader=FileSystemLoader('.'))

def generate_newsletter_html(processed_articles, template_file="newsletter_template.html", date=""):
    """
    Generates the HTML content for the newsletter using a Jinja2 template.

    Args:
        processed_articles (list): List of processed article dictionaries.
        template_file (str): The name of the Jinja2 HTML template file.
        date (str): The date string to display in the newsletter title.

    Returns:
        str: The rendered HTML content of the newsletter.
    """
    template = env.get_template(template_file)

    # Group articles by sector for better organization in the newsletter
    articles_by_sector = {sector: [] for sector in SECTORS.keys()}
    for article in processed_articles:
        for sector in article['sectors']:
            if sector in articles_by_sector:
                articles_by_sector[sector].append(article)

    # Filter out empty sectors so they don't appear in the newsletter
    filtered_articles_by_sector = {
        sector: articles for sector, articles in articles_by_sector.items() if articles
    }

    # Render the template with the grouped articles and date
    return template.render(articles_by_sector=filtered_articles_by_sector, date=date)

# --- Main Workflow ---
def main_workflow():
    """
    Orchestrates the entire newsletter generation process:
    fetches news, processes it, generates HTML, and displays it.
    """
    # Define your API Key and Sectors here
    # IMPORTANT: Replace "YOUR_NEWSAPI_KEY" with your actual NewsAPI.org key
    NEWS_API_KEY = "72780b49c21d48148218edc1733ff9c0"

    # Define your sectors and associated keywords (expanded for better coverage)
    global SECTORS # Declare global to modify the global SECTORS dictionary
    SECTORS = {
        "Technology": ["tech", "software", "hardware", "AI", "startup", "semiconductor", "cloud computing", "fintech", "blockchain", "cybersecurity", "innovation"],
        "Pharmaceuticals": ["pharma", "drug", "biotech", "clinical trial", "vaccine", "healthcare", "medicine", "biotechnology", "FDA", "R&D"],
        "Energy": ["oil", "gas", "renewable", "solar", "wind", "energy market", "crude", "drilling", "utilities", "power grid", "ESG"],
        "Automotive": ["auto", "electric vehicle", "car", "tesla", "manufacturing", "automaker", "EV", "autonomous driving", "mobility"],
        "Finance": ["bank", "investment", "fund", "stock", "bond", "forex", "economy", "market", "currency", "financial", "securities", "trading", "merger", "acquisition", "IPO", "earnings", "interest rate", "inflation", "recession"],
        "Real Estate": ["real estate", "property", "housing", "mortgage", "construction", "REIT", "commercial property", "residential market"],
        "Retail": ["retail", "e-commerce", "consumer goods", "fashion", "supermarket", "shopping", "online sales"],
        # Add more specific financial sectors if desired
    }

    today = datetime.date.today().strftime("%Y-%m-%d")
    print(f"Running financial newsletter bot for {today}")

    # 1. Pull news (using NewsAPI.org example)
    # Using a more targeted query and negative keywords to filter out irrelevant news
    print("Fetching articles from NewsAPI...")
    try:
        finance_news = get_newsapi_articles(
            NEWS_API_KEY,
            query="financial markets OR stock market OR investment OR economy OR corporate finance OR tech finance OR energy finance OR pharma finance OR real estate finance OR retail finance -casino -gambling -sports -entertainment -celebrity",
            language="en",
            page_size=50 # Increased page_size to get more articles
        )
        print(f"Pulled {len(finance_news)} raw articles.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news from API: {e}")
        print("Please check your API key, internet connection, or API rate limits.")
        return # Exit if news fetching fails

    # 2. Process and categorize
    print("Processing and categorizing articles...")
    processed_articles = process_articles(finance_news, SECTORS)
    print(f"Found {len(processed_articles)} relevant articles after processing.")

    if not processed_articles:
        print("No relevant articles found for today's newsletter after categorization. Exiting.")
        return # Exit if no relevant articles

    # Optional: Print processed articles for review in the console
    print("\n--- Processed Articles (for console review) ---")
    for article in processed_articles:
        print(f"Title: {article['title']}\nLink: {article['link']}\nSectors: {article['sectors']}\nSummary: {article['generated_summary']}\n---")
    print("-----------------------------------------------\n")

    # 3. Generate HTML
    print("Generating HTML newsletter...")
    html_newsletter_content = generate_newsletter_html(processed_articles, date=today)

    # 4. Save to a file and open in browser
    output_filename = f"financial_newsletter_{today}.html"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(html_newsletter_content)
        print(f"Newsletter saved to {output_filename}")

        # Automatically open the file in the default web browser
        # This works on Windows, macOS, and Linux (though behavior might vary slightly)
        os.startfile(output_filename) # Windows specific, but generally works
        # For cross-platform, you might use:
        # import webbrowser
        # webbrowser.open(output_filename)
        print("Opening newsletter in default web browser...")

    except Exception as e:
        print(f"Error saving or opening newsletter file: {e}")

# --- Entry Point ---
if __name__ == "__main__":
    main_workflow()