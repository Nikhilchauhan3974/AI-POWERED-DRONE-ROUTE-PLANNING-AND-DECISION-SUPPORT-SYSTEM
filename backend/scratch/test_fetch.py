import urllib.request
import json
import ssl

# Bypass SSL verification if needed for local test environment
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    "https://raw.githubusercontent.com/nswamy14/geoJson/master/indianCitiesLatLong.json",
    "https://raw.githubusercontent.com/sandeepbaid/indian-cities-states-list/master/cities.json",
    "https://raw.githubusercontent.com/dastagirkhan/00a6f6e32425e0944241/raw/d84b067f9dc6e86fbfa7db8f15ab5eb6297312f1/cities.json"
]

for url in urls:
    print(f"--- Fetching: {url} ---")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode('utf-8'))
            print("Type:", type(data))
            if isinstance(data, list) and len(data) > 0:
                print("First item:", json.dumps(data[0], indent=2))
                print("Total items:", len(data))
            elif isinstance(data, dict):
                print("Keys:", list(data.keys())[:5])
                first_key = list(data.keys())[0]
                print(f"First key '{first_key}':", data[first_key])
    except Exception as e:
        print("Error:", e)
