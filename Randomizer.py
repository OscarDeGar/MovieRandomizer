import pandas as pd
import random

def load_and_prepare_df(csv_path):
    # Load the CSV
    df = pd.read_csv(csv_path)

    # Keep only rows where Type is "movie" (case‐insensitive)
    df = df[df["Type"].str.lower() == "movie"].copy()

    # Extract numeric runtime in minutes; drop rows where parsing fails
    # (expecting "Runtime" like "101 min"; extract digits)
    df["RuntimeMin"] = (
        df["Runtime"]
        .astype(str)
        .str.extract(r"(\d+)", expand=False)
        .astype(float)
    )
    df = df.dropna(subset=["RuntimeMin"])

    # Standardize Genre column to lowercase for matching
    df["GenreLower"] = df["Genre"].astype(str).str.lower()

    return df

def get_user_inputs():
    # Ask for minimum runtime; blank → default 0
    raw_min = input("Enter minimum runtime (in minutes) [press ENTER to default to 0]: ").strip()
    if raw_min == "":
        min_rt = 0
    else:
        try:
            min_rt = int(raw_min)
            if min_rt < 0:
                print("Negative detected; defaulting minimum runtime to 0.")
                min_rt = 0
        except ValueError:
            print("Invalid input; defaulting minimum runtime to 0.")
            min_rt = 0

    # Ask for maximum runtime; blank → default a large number (e.g., 9999)
    raw_max = input("Enter maximum runtime (in minutes) [press ENTER to default to 9999]: ").strip()
    if raw_max == "":
        max_rt = 9999
    else:
        try:
            max_rt = int(raw_max)
            if max_rt < 0:
                print("Negative detected; defaulting maximum runtime to 9999.")
                max_rt = 9999
        except ValueError:
            print("Invalid input; defaulting maximum runtime to 9999.")
            max_rt = 9999

    if min_rt > max_rt:
        print("Minimum exceeds maximum; swapping values.")
        min_rt, max_rt = max_rt, min_rt

    # Ask for comma‐separated genres or "skip"; blank → skip
    raw = input(
        "Enter one or more genres (comma‐separated), e.g. 'action, comedy',\n"
        "or press ENTER to skip genre filtering: "
    ).strip().lower()

    if raw == "" or raw == "skip":
        genre_terms = ["skip"]
    else:
        # Split on comma, strip whitespace, remove empty
        genre_terms = [g.strip() for g in raw.split(",") if g.strip()]
        if not genre_terms:
            genre_terms = ["skip"]

    return min_rt, max_rt, genre_terms

def filter_movies(df, min_rt, max_rt, genre_terms):
    # 1) Filter by runtime
    filtered = df[(df["RuntimeMin"] >= min_rt) & (df["RuntimeMin"] <= max_rt)].copy()

    # 2) If the user provided actual genres (not just ["skip"]), keep movies
    #    where ALL of the genre_terms appear in that row's "GenreLower"
    if genre_terms != ["skip"]:
        def matches_all(genres_lower: str):
            return all(term in genres_lower for term in genre_terms)

        filtered = filtered[filtered["GenreLower"].apply(matches_all)].copy()

    return filtered

def suggest_random_movies(df, n=3):
    total = len(df)
    if total == 0:
        print("\nNo movies available.")
        return

    if total <= n:
        print(f"\nOnly {total} movie(s) available. Displaying all:")
        for _, row in df.iterrows():
            print(f"• {row['Name']} ({int(row['RuntimeMin'])} min) – Genres: {row['Genre']}")
    else:
        sample = df.sample(n).reset_index(drop=True)
        print(f"\nHere are {n} random movie suggestions:")
        for i, row in sample.iterrows():
            print(f"{i+1}. {row['Name']} ({int(row['RuntimeMin'])} min) – Genres: {row['Genre']}")

def main():
    csv_path = "Data/watchlist_with_metadata.csv"  # adjust if needed
    df = load_and_prepare_df(csv_path)

    init = input("Would you like to apply filters? (yes/no): ").strip().lower()
    if init.startswith("y"):
        min_rt, max_rt, genre_terms = get_user_inputs()
        print(f"\nFiltering for runtimes between {min_rt} and {max_rt} minutes", end="")
        if genre_terms != ["skip"]:
            print(f", and genres: {', '.join(genre_terms)}")
        else:
            print(", no genre filter.")
        filtered = filter_movies(df, min_rt, max_rt, genre_terms)
        suggest_random_movies(filtered, n=3)
    else:
        # No filtering: pick any random movie
        print("\nNo filters applied. Picking a random movie from all:")
        suggest_random_movies(df, n=3)

if __name__ == "__main__":
    main()
