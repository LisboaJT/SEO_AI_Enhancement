import os

# Configuration settings
DATABASE_URI = 'sqlite:///data/mydatabase.db'
API_KEY = os.getenv('OPENAI_API_KEY')
MAX_API_CALLS_PER_DAY = 8000
WP_API_KEY = os.getenv('WP_API_KEY')

# Paths
CSV_INPUT_PATH = 'data/2024-02-05-yoast-seo-keywords.csv'
CSV_OUTPUT_PATH = 'data/2024-02-05-yoast-seo-keywords.csv-updated.csv'
CSV_OUTPUT_PATH_QC_DONE = 'data/2024-02-05-yoast-seo-keywords-qc-done.csv'
CSV_OUTPUT_PATH_QC_LAST = 'data/2024-02-05-yoast-seo-keywords-qc-done-last.csv'
CSV_OUTPUT_PATH_QC_CLEAN = 'data/2024-02-05-yoast-seo-keywords-qc-done-last-clean.csv'

# Add a delay time in seconds
RATE_LIMIT_DELAY = .5
