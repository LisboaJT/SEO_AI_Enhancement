import os

# Configuration settings
DATABASE_URI = 'sqlite:///data/mydatabase.db'
API_KEY = os.getenv('OPENAI_API_KEY')
MAX_API_CALLS_PER_DAY = 8000
WP_API_KEY = os.getenv('WP_API_KEY')

# Paths
CSV_INPUT_PATH = 'data/2024-02-05-yoast-seo-keywords.csv'
CSV_OUTPUT_PATH = 'data/2024-02-05-yoast-seo-keywords.csv-updated.csv'

# Add a delay time in seconds
RATE_LIMIT_DELAY = .5
