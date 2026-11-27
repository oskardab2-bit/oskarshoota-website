"""Aktualisiert public/refs.json + Cover aus der Spotify-Playlist und lädt fehlende Bilder.
Läuft täglich per GitHub Action. Entfernte Playlist-Songs verschwinden von der Website."""
import io, json, os, re, sys, urllib.request
from PIL import Image

PL = "5U6D11LRlH7k8QjRR3xY4q"
OUT = "public"
STATIC = {  # einmalig geladene Bilder
    "about/studio.jpg": ("https://cdn.sumup.store/shops/71325985/settings/c08f85fe-7799-4875-b5ce-7617326b7ee4.jpeg", 1200),
    "about/cert1.jpg": ("https://cdn.sumup.store/shops/71325985/settings/th1024/911eff00-0a4b-4416-a44a-b7d6acdc25d2.jpeg", 800),
    "about/cert2.jpg": ("https://cdn.sumup.store/shops/71325985/settings/th1024/c1124ab9-89e8-4289-9312-49e91d03a6ae.jpeg", 800),
    "about/cert3.jpg": ("https://cdn.sumup.store/shops/71325985/settings/th1024/3bbd5c23-8d36-4356-b41c-f1356269f933.jpeg", 800),
    "about/cert4.jpg": ("https://cdn.sumup.store/shops/71325985/settings/th1024/ad5bd7ca-e22a-407e-ac8a-8ac14fd28f7b.jpeg", 800),
}
for vid in ["1idfAXSg4TI", "7HkOQiWDvoI", "gfKv2TBMo3Y", "VdUY7wLOW5I", "ZvBTj_SvRoU", "aUiBYLatuAU"]:
    STATIC[f"beats/{vid}.jpg"] = (f"https://i.ytimg.com/vi/{vid}/mqdefault.jpg", 320)


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read()


def save_img(data, path, size):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img = Image.open(io.BytesIO(data)).convert("RGB")
    img.thumbnail((size, size))
    img.save(path, "JPEG", quality=82, optimize=True)


for rel, (url, size) in STATIC.items():
    if not os.path.exists(f"{OUT}/{rel}"):
        try:
            save_img(get(url), f"{OUT}/{rel}", size)
        except Exception as e:
            print("Bild fehlgeschlagen:", rel, e)

html = get(f"https://open.spotify.com/embed/playlist/{PL}").decode()
data = json.loads(re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S).group(1))
tracks = data["props"]["pageProps"]["state"]["data"]["entity"]["trackList"]
if not tracks:
    sys.exit("Playlist leer oder nicht lesbar – nichts geändert.")

refs, keep = [], set()
for t in tracks:
    tid = t["uri"].split(":")[-1]
    rel = f"covers/{tid}.jpg"
    keep.add(f"{tid}.jpg")
    if not os.path.exists(f"{OUT}/{rel}"):
        o = json.loads(get(f"https://open.spotify.com/oembed?url=spotify:track:{tid}"))
        save_img(get(o["thumbnail_url"]), f"{OUT}/{rel}", 360)
    refs.append({"id": tid, "title": t["title"], "artists": t["subtitle"],
                 "url": f"https://open.spotify.com/track/{tid}", "cover": rel})
refs.reverse()  # neueste zuerst

for f in os.listdir(f"{OUT}/covers"):
    if f not in keep:
        os.remove(f"{OUT}/covers/{f}")

with open(f"{OUT}/refs.json", "w", encoding="utf-8") as fh:
    json.dump({"playlist": f"https://open.spotify.com/playlist/{PL}", "tracks": refs}, fh, ensure_ascii=False, indent=1)
print(len(refs), "Songs")
