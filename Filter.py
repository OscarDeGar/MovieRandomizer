import pandas as pd

def load_and_prepare_df(csv_path):
    """
    Load the CSV of watchlist with metadata, keep only movies,
    extract numeric runtime in minutes, and lowercase genres.
    """
    df = pd.read_csv(csv_path)

    # Keep only rows where Type is "movie" (case-insensitive)
    df = df[df["Type"].str.lower() == "movie"].copy()

    # Extract numeric runtime in minutes; drop rows where parsing fails
    # (expects "Runtime" like "101 min"; extract the digits)
    df["RuntimeMin"] = (
        df["Runtime"]
        .astype(str)
        .str.extract(r"(\d+)", expand=False)
        .astype(float)
    )
    df = df.dropna(subset=["RuntimeMin"])

    # Lowercase Genre for easier matching
    df["GenreLower"] = df["Genre"].astype(str).str.lower()
    return df

def get_search_inputs():
    """
    Prompt the user for search criteria:
    - min runtime (default 0 if blank)
    - max runtime (default very large if blank)
    - comma-separated list of genres (or blank to skip)
    """
    # Minimum runtime
    raw_min = input("Enter minimum runtime in minutes [ENTER for 0]: ").strip()
    if raw_min == "":
        min_rt = 0
    else:
        try:
            min_rt = int(raw_min)
            if min_rt < 0:
                print("Negative minimum detected; defaulting to 0.")
                min_rt = 0
        except ValueError:
            print("Invalid input; defaulting minimum to 0.")
            min_rt = 0

    # Maximum runtime
    raw_max = input("Enter maximum runtime in minutes [ENTER for no upper bound]: ").strip()
    if raw_max == "":
        max_rt = 9999
    else:
        try:
            max_rt = int(raw_max)
            if max_rt < 0:
                print("Negative maximum detected; defaulting to 9999.")
                max_rt = 9999
        except ValueError:
            print("Invalid input; defaulting maximum to 9999.")
            max_rt = 9999

    if min_rt > max_rt:
        print("Minimum exceeds maximum; swapping values.")
        min_rt, max_rt = max_rt, min_rt

    # Genre list
    raw_genres = input(
        "Enter one or more genres (comma-separated, e.g. 'action, comedy'),\n"
        "or press ENTER to skip genre filtering: "
    ).strip().lower()

    if raw_genres in ("", "skip"):
        genre_terms = []
    else:
        # Split on comma, strip whitespace, ignore empty strings
        genre_terms = [g.strip() for g in raw_genres.split(" ") if g.strip()]

    return min_rt, max_rt, genre_terms

def filter_movies(df, min_rt, max_rt, genre_terms):
    """
    Return a DataFrame filtered by:
    - RuntimeMin between min_rt and max_rt (inclusive)
    - If genre_terms nonempty, only rows where ALL terms appear in GenreLower
    """
    filtered = df[(df["RuntimeMin"] >= min_rt) & (df["RuntimeMin"] <= max_rt)].copy()

    if genre_terms:
        def matches_all(genres_lower: str):
            return all(term in genres_lower for term in genre_terms)
        filtered = filtered[filtered["GenreLower"].apply(matches_all)].copy()

    return filtered

def print_matching_movies(filtered_df):
    """
    Print out all matching movies (Name, Year, Runtime, Genre).
    """
    count = len(filtered_df)
    if count == 0:
        print("\nNo movies match your criteria.")
        return

    print(f"\nFound {count} matching movie(s):\n")
    for _, row in filtered_df.iterrows():
        name = row["Name"]
        year = row.get("OMDbYear", row.get("Year", "N/A"))
        runtime = f"{int(row['RuntimeMin'])} min"
        genre = row["Genre"]
        print(f"• {name} ({year}) — {runtime} — Genres: {genre}")
    print()

def main():
    csv_path = "Data/watchlist_with_metadata.csv"  # adjust if needed
    df = load_and_prepare_df(csv_path)

    print("SEARCH MOVIES BY RUNTIME & GENRE\n")
    min_rt, max_rt, genre_terms = get_search_inputs()

    print(f"\nFiltering for runtime between {min_rt} and {max_rt} minutes", end="")
    if genre_terms:
        print(f", requiring genres: {', '.join(genre_terms)}")
    else:
        print(", no genre filter.")
    filtered = filter_movies(df, min_rt, max_rt, genre_terms)
    print_matching_movies(filtered)

if __name__ == "__main__":
    main()
