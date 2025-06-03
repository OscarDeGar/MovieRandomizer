import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import sys
from bs4 import BeautifulSoup
from parse import parse_media

# Load the CSV with a column "Letterboxd URI"
csv_path = 'Data/watchlist.csv'  # replace with your CSV path
df = pd.read_csv(csv_path)

# Function to fetch and parse HTML content from a Letterboxd URL
def scrape_letterboxd_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # raise an error on bad status
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup  # or return soup.prettify() if you want full HTML string
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Prepare empty lists for new columns
titles = []
years = []
directors_list = []
genres_list = []
ratings = []
runtimes = []


# Iterate over each row, scrape & parse, then sleep a random interval between 2–10 seconds
for idx, uri in enumerate(df['Letterboxd URI']):
    try:
        soup = scrape_letterboxd_html(uri)
        if not soup:
            raise Exception("Failed to retrieve or parse HTML")

        data = parse_media(soup)
        df.at[idx, 'Title'] = data["Title"]
        df.at[idx, 'Year'] = data["Year"]
        df.at[idx, 'Directors'] = "; ".join(data["Directors"]) if data["Directors"] else None
        df.at[idx, 'Genres'] = "; ".join(data["Genres"]) if data["Genres"] else None
        df.at[idx, 'AverageRating'] = data["AverageRating"]
        df.at[idx, 'Runtime'] = data["Runtime"]

        print(f"[{idx+1}/{len(df)}] Done: {data['Title']}")
        # Random sleep between 2 and 10 seconds
        time.sleep(random.uniform(2, 10))

    except Exception as e:
        print(f"Error processing row {idx+1} (URL: {uri}): {e}", file=sys.stderr)
        # Save current progress and exit
        df.to_csv('Data/watchlist_with_metadata_partial.csv', index=False)
        print("Saved partial results to 'watchlist_with_metadata_partial.csv'. Exiting.", file=sys.stderr)
        sys.exit(1)

# If loop completes without exception, save full results
df.to_csv('Data/watchlist_with_metadata.csv', index=False)
print("All done! Results saved to 'watchlist_with_metadata.csv'")

# # Scrape the first URL in the "Letterboxd URI" column
# out = scrape_letterboxd_html(df['Letterboxd URI'].iloc[0])

# data = parse_media(out)

# # Write the prettified HTML (string) to disk  
# if out is not None:
#     with open('output.html', 'w', encoding='utf-8') as f:
#         f.write(out.prettify())
