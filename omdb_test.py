import requests

# 1) Put your OMDb key here
OMDB_API_KEY = "93259abe"

# 2) The title you want to test
test_title = "Inception"

# 3) Build the parameters dict exactly as OMDb expects
params = {
    "apikey": OMDB_API_KEY,
    "t": "Peeping Tom",
    "y": 1960
}

# 4) Make the GET request
response = requests.get("http://www.omdbapi.com/", params=params)

# 5) Print out the exact URL for debugging
print("OMDb request URL:", response.url)
print("Status code:", response.status_code)

# 6) Try to parse JSON (or print raw text if JSON fails)
try:
    data = response.json()
    print("Raw JSON response:", data)
except ValueError:
    print("Response not JSON. Raw text:")
    print(response.text)
