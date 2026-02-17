import os
import django
import requests
import time
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile

# ---------------- DJANGO SETUP ----------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from tourism.models import Category, TouristPlace

HEADERS = {
    "User-Agent": "SikkimAITourism/1.0 (Academic Project)"
}

WIKIMEDIA_API = "https://commons.wikimedia.org/w/api.php"


def fetch_wikimedia_image(query):
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"intitle:{query}",
        "gsrlimit": 3,
        "gsrnamespace": 6,
        "prop": "imageinfo",
        "iiprop": "url"
    }

    r = requests.get(WIKIMEDIA_API, params=params, headers=HEADERS, timeout=20)
    r.raise_for_status()

    pages = r.json().get("query", {}).get("pages", {})
    for page in pages.values():
        info = page.get("imageinfo")
        if info:
            return info[0]["url"]

    return None


def download_and_convert_image(url):
    r = requests.get(url, headers=HEADERS, timeout=20, stream=True)
    r.raise_for_status()

    content_type = r.headers.get("Content-Type", "")
    if not content_type.startswith("image/"):
        return None

    image_bytes = r.content

    try:
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
    except Exception:
        return None

    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return buffer.getvalue()


def bulk_upload():
    print("\n--- CATEGORY IMAGES ---\n")

    for category in Category.objects.all():
        try:
            print(f"Fetching category image: {category.name}")
            url = fetch_wikimedia_image(f"{category.name} Sikkim")

            if not url:
                print("No image URL found")
                continue

            img_data = download_and_convert_image(url)
            if not img_data:
                print("Invalid image skipped")
                continue

            category.image.save(
                f"category_{category.id}.jpg",
                ContentFile(img_data),
                save=True
            )

            print("Saved successfully")
            time.sleep(1)

        except Exception as e:
            print(f"Error for {category.name}: {e}")

    print("\n--- TOURIST PLACE IMAGES ---\n")

    for place in TouristPlace.objects.all():
        try:
            print(f"Fetching place image: {place.name}")
            url = fetch_wikimedia_image(f"{place.name} Sikkim India")

            if not url:
                print("No image URL found")
                continue

            img_data = download_and_convert_image(url)
            if not img_data:
                print("Invalid image skipped")
                continue

            place.image_main.save(
                f"place_{place.id}.jpg",
                ContentFile(img_data),
                save=True
            )

            print("Saved successfully")
            time.sleep(1)

        except Exception as e:
            print(f"Error for {place.name}: {e}")


if __name__ == "__main__":
    bulk_upload()
