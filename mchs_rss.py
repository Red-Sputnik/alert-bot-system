import requests
import xml.etree.ElementTree as ET
from typing import List, Dict
from regions import REGIONS

RSS_URL = "https://mchs.gov.ru/deyatelnost/press-centr/vnimanie/rss"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8",
}

def fetch_rss() -> str:
    response = requests.get(
        RSS_URL,
        headers=HEADERS,
        timeout=10
    )
    response.raise_for_status()
    return response.text


def parse_rss(xml_data: str) -> List[Dict]:
    root = ET.fromstring(xml_data)
    items = []

    for item in root.findall("./channel/item"):
        title = item.findtext("title", "")
        link = item.findtext("link", "")
        pub_date = item.findtext("pubDate", "")

        full_text = ""
        for elem in item:
            if "full-text" in elem.tag:
                full_text = elem.text or ""

        items.append({
            "title": title,
            "link": link,
            "pub_date": pub_date,
            "text": full_text
        })

    return items

def extract_regions(text: str) -> List[str]:
    found = []

    for _, region in REGIONS.items():
        if region.lower() in text.lower():
            found.append(region)

    return list(set(found))

def get_events() -> List[Dict]:
    xml_data = fetch_rss()
    items = parse_rss(xml_data)

    events = []
    for item in items:
        regions = extract_regions(item["title"] + " " + item["text"])
        if regions:
            events.append({
                "title": item["title"],
                "link": item["link"],
                "pub_date": item["pub_date"],
                "regions": regions
            })

    return events
