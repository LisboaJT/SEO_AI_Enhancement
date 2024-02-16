import pandas as pd
import re
import spacy
from openai import OpenAI
from config import CSV_INPUT_PATH, CSV_OUTPUT_PATH_QC_DONE, API_KEY
from utils import scrape_webpage

nlp = spacy.load('en_core_web_sm')
df = pd.read_csv(CSV_INPUT_PATH)
client = OpenAI(api_key=API_KEY)


def debug_decorator(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result}")
        return result
    return wrapper

def mechanical_text_checks(text):
    issues = []

    # Check for first letter capitalization
    if text[0].islower():
        issues.append("First letter is not capitalized.")

    # Check for odd punctuation
    self_reference = ['SEO', 'Description']
    for terms in self_reference:
        if terms in text:
            issues.append(f"Contains odd punctuation: {terms}")

    # Check for multiple lines of text (assuming \n indicates a new line)
    if '\n' in text or '\r' in text:
        issues.append("Contains multiple lines of text.")

    # Check for multiple periods, which might indicate multiple sentences
    # if text.count('.') > 3:
    #     issues.append("Contains multiple periods, indicating possible multiple sentences.")

    return issues if issues else ["No issues detected."]


def process_text_entries(text_entries):
    for text in text_entries:
        issues = mechanical_text_checks(text)
        if "No issues detected." in issues:
            print(f"Text passes checks: {text}")
        else:
            print(f"Issues found in text: {text}")
            for issue in issues:
                print(f"- {issue}")
            # Here, you could call a revision function or take other corrective actions


def check_and_report_issues(text, field_name, row_index):
    issues = mechanical_text_checks(text)
    if issues != ["No issues detected."]:
        print(f"Issues in row {row_index} {field_name}: {issues}")
        return True  # Return True if issues found
    return False  # Return False if no issues found


@debug_decorator
def revise_meta_description(title, text, client):
    if text is None:
        text = "No Info Provided"

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user",
                       "content": "This is a final revision for the problem entries to my list. I need you to write an "
                                  "SEO friendly meta description of no more than 150 characters that describes the "
                                  "text. Please use complete sentences, plain english, and no special characters."
                                  "Try to make the descriptions unique and reflective of the content and tone. "
                                  "Please use the themes of RVA Magazine, focusing on art, music, culture, "
                                  "food, nightlife, and politics of Richmond Virginia.  "
                                  "The initial meta description did not meet our standards due to reasons "
                                  "such as incorrect grammar, bad format style, overly long description, "
                                  "or multiple lines of text. "
                                  "Here are a few examples of good meta descriptions: "
                                  "'Lewis Ginter Botanical Garden's Dominion Energy GardenFest of Lights features over "
                                  "a million lights illuminating stunning art exhibits, including works by Van Gogh "
                                  "and Bob Ross, making it a must-see holiday experience in Richmond, VA.'"
                                  "'Join students and legislators in Richmond this Friday for the Second National "
                                  "School Walkout, as they rally to end gun violence in schools and demand action "
                                  "from legislators - RVA Mag.'"
                                  "'Will the West Virginia teacher strike inspire educators in Virginia to join the "
                                  "fight? Find out the impact of this historic statewide strike on Richmond's "
                                  "education system and its teachers.'"
                                  "To better align with our audience's expectations and improve search engine "
                                  "visibility, we require a revised meta description. "
                                  "This should succinctly summarize the article's content while incorporating key "
                                  "themes of art, music, culture, food, nightlife, and politics specific to Richmond, "
                                  "Virginia. Again, the description should be 2 to three professional, concise, "
                                  "SEO-friendly sentences that are strictly no longer than 150 characters."
                                  f"\n{title}"
                                  f"\n{text}"}],
            model="gpt-4",
            max_tokens=150
        )
        return completion.choices[0].message.content.strip() if completion.choices else 'Failed to generate description'
    except Exception as e:
        print(f"Error during API call: {e}")
        return 'Failed to generate description'


@debug_decorator
def revise_seo_title(title, text, client):
    if text is None:
        text = "No Info Provided"

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user",
                       "content": "This is a final revision for the problem entries to my list. I need you to write an "
                                  "SEO friendly meta description of no more than 150 characters that describes the "
                                  "text. Please use complete sentences, plain english, and no special characters."
                                  "Try to make the descriptions unique and reflective of the content and tone. "
                                  "Using the page title and text below, "
                                  "write 1 short SEO Title of a strict maximum of 60 characters. "
                                  "NO quotes around the titles written! "
                                  "Don't use phrases like 'Join us', instead use 'Check out' as events are often hosted"
                                  " by other groups. "
                                  "Try to make the titles unique and reflective of the content. "
                                  "Please use the themes of RVA Magazine, focusing on art, music, culture, "
                                  "food, nightlife, and politics of Richmond Virginia.  "
                                  "We've identified issues with the previously generated SEO title for this entry and "
                                  "need a revised version that better captures the essence of the content, is concise, "
                                  "and directly relevant to the target audience. The original title may have been "
                                  "mis-formatted, lacked focus, or missed key aspects of the content. Based on the "
                                  "article's content and considering the themes of art, music, culture, food, "
                                  "nightlife, and politics in Richmond, Virginia, please generate a revised SEO title "
                                  "that is engaging, precise, and limited to 60 characters."
                                  "Here are examples of good titles:"
                                  "'Neon Nostalgia Lost: Circuit Arcade Bar's Mural Vanished'"
                                  "'Lofties: Richmond's Dreamy Experimental Bedroom Pop Duo'"
                                  "'McKinley Dixon, Big Baby & More at Dominion Riverrock 2018'"
                                  f"The page title and text start here:\n{title}\n{text}"}],
            model="gpt-4",
            max_tokens=50
        )
        return completion.choices[
            0].message.content.strip() if completion.choices else 'Failed to generate description'
    except Exception as e:
        print(f"Error during API call: {e}")
        return 'Failed to generate description'



def correct_and_update_row(df, index, client):
    row = df.loc[index]
    url = row['url']

    # Step 1: Re-scrape the webpage
    title, body_text = scrape_webpage(url)
    if not title or not body_text:
        print(f"Failed to re-scrape {url}")
        return False  # Indicating correction was not successful

    # Step 2: Request revision for meta_description and seo_title
    revised_meta_description = revise_meta_description(title, body_text[:1000], client)
    revised_seo_title = revise_seo_title(title, body_text[:500], client)

    # Step 3: Update the DataFrame
    df.at[index, 'title'] = title
    df.at[index, 'meta_description'] = revised_meta_description
    df.at[index, 'seo_title'] = revised_seo_title
    return True  # Indicating successful correction


for index, row in df.iterrows():
    if 'tags' in row['url']:
        continue

    # Check for issues
    meta_description_issues = check_and_report_issues(row['meta_description'], 'meta_description', index + 1)
    seo_title_issues = check_and_report_issues(row['seo_title'], 'seo_title', index + 1)

    # If any issues are detected, attempt correction
    if meta_description_issues or seo_title_issues:
        success = correct_and_update_row(df, index, client)  # Ensure this function is defined to accept these parameters
        if success:
            print(f"Row {index + 1} corrected.")
        else:
            print(f"Failed to correct row {index + 1}.")
    else:
        print(f"Row {index + 1} has no issues.")

df.to_csv(CSV_OUTPUT_PATH_QC_DONE, index=False)
