import pandas as pd
import requests
import time
import random

# 1) Configuration: put your own OMDb key here
OMDB_API_KEY = '93259abe'

# 2) Load your existing watchlist CSV (must have a "Title" column)
csv_in_path = "Data/watchlist.csv"   # adjust to your file path
df = pd.read_csv(csv_in_path)

# 3) Prepare new columns (fill with None by default)
df["Year"] = None
df["Type"] = None        # "movie" or "series"
df["Genre"] = None       # e.g. "Action, Drama"
df["IMDbRating"] = None  # e.g. "7.5"
df["Runtime"] = None     # e.g. "120 min"

# 4) OMDb base URL
OMDB_URL = "http://www.omdbapi.com/"

# 5) Function to query OMDb by title + year (always include "y")
def fetch_omdb_by_title_and_year(title, year):
    params = {
        "apikey": OMDB_API_KEY,
        "t": title,
        "y": year
    }
    print(f"Querying OMDb with: {params}")
    resp = requests.get(OMDB_URL, params=params)
    if resp.status_code != 200:
        return None
    data = resp.json()
    if data.get("Response", "False") == "False":
        return None
    return data

# 6) Iterate over each row, query OMDb, fill columns
for idx, row in df.iterrows():
    title = str(row.get("Name", "")).strip()
    year  = str(row.get("Year", "")).strip()
    print(f"[{idx+1}/{len(df)}] Title: '{title}' | CSV Year: '{year}'")

    if not title or not year:
        print(f"[{idx+1}/{len(df)}] Missing Title or Year—skipping.")
        continue

    omdb_data = fetch_omdb_by_title_and_year(title, year)
    if omdb_data is None:
        print(f"[{idx+1}/{len(df)}] OMDb lookup failed for '{title}' ({year}).")
    else:
        df.at[idx, "OMDbYear"]    = omdb_data.get("Year")
        df.at[idx, "Type"]       = omdb_data.get("Type")
        df.at[idx, "Genre"]      = omdb_data.get("Genre")
        df.at[idx, "IMDbRating"] = omdb_data.get("imdbRating")
        df.at[idx, "Runtime"]    = omdb_data.get("Runtime")
        print(
            f"[{idx+1}/{len(df)}] Fetched → "
            f"OMDbYear={omdb_data.get('Year')} | "
            f"Type={omdb_data.get('Type')} | "
            f"Genre={omdb_data.get('Genre')} | "
            f"IMDbRating={omdb_data.get('imdbRating')} | "
            f"Runtime={omdb_data.get('Runtime')}"
        )

    # 7) Random delay between 2 and 10 seconds
    # time.sleep(random.uniform(2.0, 10.0))

# 8) Save the augmented DataFrame to a new CSV
out_path = "Data/watchlist_with_metadata.csv"
df.to_csv(out_path, index=False)
print(f"\nFinished! Saved results to: {out_path}")
