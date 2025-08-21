import re
from typing import Dict, List, Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from cachetools import TTLCache


class TractorGuruClient:
    """
    Lightweight HTML client for TractorGuru public pages.
    Notes:
    - This uses scraping of publicly available pages because no official public API exists.
    - Respect site performance: basic in-process caching and conservative timeouts.
    - Selectors are best-effort and may need updates if the site structure changes.
    """

    def __init__(self, base_url: str = "https://tractorguru.in") -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })

        # Cache pages and parsed results for 1 day
        self._page_cache: TTLCache[str, str] = TTLCache(maxsize=128, ttl=60 * 60 * 24)
        self._brands_cache: TTLCache[str, List[Dict[str, Any]]] = TTLCache(maxsize=1, ttl=60 * 60 * 24)
        self._models_cache: TTLCache[str, List[Dict[str, Any]]] = TTLCache(maxsize=128, ttl=60 * 60 * 24)
        self._details_cache: TTLCache[str, Dict[str, Any]] = TTLCache(maxsize=256, ttl=60 * 60 * 24)

    def _fetch(self, path_or_url: str) -> str:
        url = path_or_url
        if not path_or_url.startswith("http"):
            path = path_or_url if path_or_url.startswith("/") else f"/{path_or_url}"
            url = urljoin(self.base_url + "/", path.lstrip("/"))

        if url in self._page_cache:
            return self._page_cache[url]

        response = self.session.get(url, timeout=15)
        response.raise_for_status()
        html = response.text
        self._page_cache[url] = html
        return html

    def get_brands(self) -> List[Dict[str, Any]]:
        if "brands" in self._brands_cache:
            return self._brands_cache["brands"]

        # Try common brands listing paths
        possible_paths = [
            "/tractor-brands",
            "/tractor-brand",
            "/tractor/brands",
        ]

        html = None
        for path in possible_paths:
            try:
                html = self._fetch(path)
                if html and len(html) > 500:
                    break
            except Exception:
                continue

        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        brand_links = []

        # Heuristics: anchors that link to brand pages
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            text = a.get_text(strip=True)
            if not text:
                continue
            # Likely brand link patterns
            if re.search(r"/tractor-?brands?/", href, re.IGNORECASE) or re.search(r"/brand/", href, re.IGNORECASE):
                brand_links.append((text, href))

        # Fallback: cards with brand names
        if not brand_links:
            for card in soup.select('div[class*="brand"], li[class*="brand"], a[class*="brand"]'):
                if card.name == "a" and card.get("href"):
                    href = card["href"].strip()
                    text = card.get_text(strip=True)
                    if text:
                        brand_links.append((text, href))

        # Normalize and dedupe
        seen = set()
        brands: List[Dict[str, Any]] = []
        for name, href in brand_links:
            # Filter obvious non-brand links
            if len(name) < 2 or "http" in name.lower():
                continue
            slug = href
            if not slug.startswith("http"):
                slug = href if href.startswith("/") else f"/{href}"
            key = slug.rstrip("/")
            if key in seen:
                continue
            seen.add(key)
            brands.append({
                "name": name,
                "path": key,
                "url": urljoin(self.base_url + "/", key.lstrip("/")),
            })

        self._brands_cache["brands"] = brands
        return brands

    def get_brand_models(self, brand_path: str) -> List[Dict[str, Any]]:
        normalized = brand_path if brand_path.startswith("/") else f"/{brand_path}"
        cache_key = normalized.rstrip("/")
        if cache_key in self._models_cache:
            return self._models_cache[cache_key]

        html = self._fetch(cache_key)
        soup = BeautifulSoup(html, "lxml")
        models: List[Dict[str, Any]] = []

        # Heuristic: model cards or links likely contain "/tractor" and a price/spec snippet
        for card in soup.select('a[href*="/tractor"], div[class*="model"], li[class*="model"]'):
            href = None
            name = None
            price = None
            img = None

            if hasattr(card, "get") and card.name == "a" and card.get("href"):
                href = card["href"].strip()
                name = card.get_text(strip=True)
            else:
                a = card.find("a", href=True)
                if a:
                    href = a["href"].strip()
                    name = a.get_text(strip=True)
                img_el = card.find("img", src=True)
                if img_el:
                    img = img_el["src"].strip()
                price_el = card.find(string=re.compile(r"₹|Rs|Price", re.IGNORECASE))
                if price_el:
                    price = price_el.strip()

            if not href or not name:
                continue

            model_path = href if href.startswith("/") else f"/{href}"
            models.append({
                "name": name,
                "path": model_path,
                "url": urljoin(self.base_url + "/", model_path.lstrip("/")),
                "thumbnail": img,
                "price": price,
            })

        # Basic dedupe by path
        deduped: Dict[str, Dict[str, Any]] = {}
        for m in models:
            deduped[m["path"]] = m
        result = list(deduped.values())
        self._models_cache[cache_key] = result
        return result

    def get_model_details(self, model_path: str) -> Dict[str, Any]:
        normalized = model_path if model_path.startswith("/") else f"/{model_path}"
        cache_key = normalized.rstrip("/")
        if cache_key in self._details_cache:
            return self._details_cache[cache_key]

        html = self._fetch(cache_key)
        soup = BeautifulSoup(html, "lxml")

        # Title
        title = soup.find("h1")
        title_text = title.get_text(strip=True) if title else soup.title.get_text(strip=True) if soup.title else ""

        # Try to parse a key-value spec table
        specs: Dict[str, Any] = {}
        for table in soup.select("table"):
            headers = [th.get_text(strip=True) for th in table.find_all("th")]
            # Look for 2-column spec tables
            if len(headers) <= 1:
                for row in table.find_all("tr"):
                    cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
                    if len(cells) == 2:
                        key, value = cells
                        if key and value:
                            specs[key] = value
            else:
                # Tables with explicit headers
                for row in table.find_all("tr"):
                    cells = [c.get_text(strip=True) for c in row.find_all("td")]
                    if len(cells) == 2:
                        key, value = cells
                        if key and value:
                            specs[key] = value

        # Try to find images
        images = [img["src"].strip() for img in soup.find_all("img", src=True) if img.get("src")]

        data = {
            "title": title_text,
            "path": cache_key,
            "url": urljoin(self.base_url + "/", cache_key.lstrip("/")),
            "specs": specs,
            "images": images[:10],
        }

        self._details_cache[cache_key] = data
        return data

