from logging import exception
from urllib.parse import urlsplit,urljoin
from bs4 import BeautifulSoup, Tag
from typing import TypedDict
import requests

class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]

def normalize_url(input_url: str) -> str:
    split_url = urlsplit(input_url)
    full_path = f"{split_url.hostname}{split_url.path}"
    full_path = full_path.rstrip("/")
    return full_path.lower()

def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.find("h1") or soup.find("h2")
    return heading.get_text(strip=True) if isinstance(heading, Tag) else ""

def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    p = soup.select_one("main p") or soup.select_one("p")
    return p.get_text(strip=True) if p else ""

def get_urls_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    urls = []
    for link in soup.find_all("a"):
        if not isinstance(link, Tag):
            continue
        href = link.get("href")
        if not href:
            continue
        urls.append(urljoin(base_url, str(href)))
    return urls

def get_images_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    urls = []
    for img in soup.find_all("img"):
        if not isinstance(img, Tag):
            continue
        src =  img.get("src")
        if not src:
            continue
        urls.append(urljoin(base_url, str(src)))
    return urls

def extract_page_data(html: str, page_url: str) -> PageData:
    return {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url)
    }
