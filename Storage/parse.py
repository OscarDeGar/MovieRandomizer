
from bs4 import BeautifulSoup
import re

def parse_media(soup):  # alias for clarity

    # 1) Film title
    title_tag = soup.find("h1", class_="headline-1 primaryname")
    film_title = title_tag.get_text(strip=True) if title_tag else None

    # 2) Release year
    year_tag = soup.find("h5", class_="date")
    release_year = None
    if year_tag:
        year_text = year_tag.get_text(strip=True)  # e.g. "07 Apr 1960"
        parts = year_text.split()
        if parts:
            # take the last token, which should be the four‐digit year
            release_year = parts[-1]


    # 3) Director name(s)
    director_list = []
    credits_block = soup.find("p", class_="credits")
    if credits_block and "Directed by" in credits_block.get_text():
        for a in credits_block.select("span.directorlist a.contributor"):
            director_list.append(a.get_text(strip=True))

    # 4) (Skipped—synopsis/tagline, if you need it you can add similar to above)

    # 5) Genres (first three)
    genres = []
    genres_block = soup.find("div", id="tab-genres")
    if genres_block:
        for a in genres_block.select("div.text-sluglist a.text-slug"):
            genres.append(a.get_text(strip=True))
    genres = genres[:3]

    # 6) Average rating (from meta-tags, if present)
    rating_meta = soup.find("meta", {"name": "twitter:data2"})
    average_rating = rating_meta["content"] if rating_meta else None

    # 7) Total runtime (e.g. "101 mins")
    runtime = None
    footer_p = soup.find("p", class_="text-link text-footer")
    if footer_p:
        text = footer_p.get_text(separator=" ", strip=True)
        # look for a pattern like "101 mins"
        m = re.search(r"(\d+\s*mins?)", text)
        if m:
            runtime = m.group(1)

    return {
        "Title": film_title,
        "Year": release_year,
        "Directors": director_list,
        "Genres": genres,
        "AverageRating": average_rating,
        "Runtime": runtime
    }

    # # Print out everything we found:
    # print("Title:", film_title)
    # print("Year:", release_year)
    # print("Director(s):", director_list)
    # print("Genres:", genres)
    # print("Average rating:", average_rating)
    # print("Runtime:", runtime)
