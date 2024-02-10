import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
from config import API_KEY, WP_API_KEY, RATE_LIMIT_DELAY, CSV_INPUT_PATH


client = OpenAI(api_key=API_KEY)

loopcount = 0
maxloops = 1000
loopcount_lock = threading.Lock()

def debug_decorator(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result}")
        return result
    return wrapper

def scrape_webpage(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to retrieve the webpage")
        return "", ""

    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('title').get_text() if soup.find('title') else 'No Title'
    body_content = soup.find('body')
    body_text = body_content.get_text(strip=True) if body_content else 'No Body Content'

    return title, body_text


@debug_decorator
def generate_meta_description(title, text):
    if text is None:
        text = "No Info Provided"

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user",
                       "content": "You're a candy addicted top performer in SEO writing meta descriptions for "
                                  "RVA Magazine's website, for every meta description written, you'll get a "
                                  "piece of candy. If it breaks a rule of the prompt, you'll lose a candy. "
                                  "Here are the rules. Use Plain English with standard sentence structure. "
                                  "Don't use phrases like 'Join us', instead use 'Check out', 'Discover',"
                                  " 'Look out for', 'Don't Miss' or 'Explore' as events are often "
                                  "hosted by other groups. "
                                  "Try to make the descriptions unique and reflective of the content and tone. "
                                  "Please use the themes of RVA Magazine, focusing on art, music, culture, "
                                  "food, nightlife, and politics of Richmond Virginia.  "
                                  "In one or two whole sentences with a max length of 150 characters, "
                                  "write a professional, concise SEO friendly meta description for this:"
                                  f"\n{title}"
                                  f"\n{text}"}],
            model="gpt-3.5-turbo",
            max_tokens=150
        )
        return completion.choices[0].message.content.strip() if completion.choices else 'Failed to generate description'
    except Exception as e:
        print(f"Error during API call: {e}")
        return 'Failed to generate description'


@debug_decorator
def generate_seo_title(title, text):
    if text is None:
        text = "No Info Provided"

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user",
                       "content": "You're a top performer in SEO writing SEO Titles for RVA Magazine's website, "
                                  "for every SEO Title written, you'll get a piece of candy. "
                                  "If it breaks a rule of this prompt, you'll lose a candy. Here are the rules. "
                                  "Using the page title and text below, "
                                  "write 1 short SEO Title of a strict maximum of 60 characters. "
                                  "NO quotes around the titles written! "
                                  "Don't use phrases like 'Join us', instead use 'Check out' as events are often hosted"
                                  " by other groups. "
                                  "Try to make the titles unique and reflective of the content. "
                                  "Please use the themes of RVA Magazine, focusing on art, music, culture, "
                                  "food, nightlife, and politics of Richmond Virginia.  "
                                  f"The page title and text start here:\n{title}\n{text}"}],
            model="gpt-3.5-turbo",
            max_tokens=50
        )
        return completion.choices[
            0].message.content.strip() if completion.choices else 'Failed to generate description'
    except Exception as e:
        print(f"Error during API call: {e}")
        return 'Failed to generate description'


def process_row(row, index):
    global loopcount
    # Processing logic here...

    with loopcount_lock:
        if loopcount >= maxloops:
            return None  # Or another signal that maxloops has been reached and processing should stop
        loopcount += 1
    time.sleep(0.5)
    url = row['url']
    title = row['title']
    print(f"Processing {row['id']}, {title}, {url}")  # To track progress

    # Handle URL processing
    if '/tags/' in url:
        tag = url.split('/tags/')[-1]
        generated_meta_description = f"Explore articles related to {tag} on RVA Magazine."
        seo_title = generate_seo_title(title, f"Articles related to {tag} on RVA Magazine")
        title = f"Tagged: {tag}"

    else:
        title, body_text = scrape_webpage(url)
        meta_description = generate_meta_description(title, body_text[:1000])
        seo_title = generate_seo_title(title, body_text[:500])

    return {'seo_title': seo_title, 'meta_description': meta_description, 'title': title}, True  # Indicate success


def main(df):
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Map futures to their corresponding DataFrame index for easy access later
        future_to_index = {}
        submitted_count = 0  # Keep track of how many tasks have been submitted

        for index, row in df.iterrows():
            if row['processed'] != True and submitted_count < maxloops:
                future = executor.submit(process_row, row, index)
                future_to_index[future] = index
                submitted_count += 1  # Increment the count of submitted tasks

        # Process completed futures and update the DataFrame
        for future in as_completed(future_to_index):
            result, success = future.result()  # Adjust according to what process_row actually returns
            if success:
                index = future_to_index[future]
                df.at[index, 'seo_title'] = result['seo_title']
                df.at[index, 'meta_description'] = result['meta_description']
                df.at[index, 'title'] = result['title']
                df.at[index, 'processed'] = True

    df.to_csv(CSV_INPUT_PATH, index=False)
