import json
import requests

URL = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"

response = requests.get(URL, timeout=60)
response.raise_for_status()
world = response.json()

pakistan = [f for f in world["features"] if f.get("id") == "PAK"]

if not pakistan:
    print("Pakistan nahi mila, file ka format badla hua hai")
else:
    with open("pakistan.geo.json", "w", encoding="utf-8") as file:
        json.dump(pakistan[0], file)
    print("Saved pakistan.geo.json | shape type:", pakistan[0]["geometry"]["type"])