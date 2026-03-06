import requests
from bs4 import BeautifulSoup
import re
import logging
import json

logger = logging.getLogger(__name__)

class BaseParser:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def get_html(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def clean_price(self, price_str):
        if not price_str:
            return None
        # Remove non-numeric characters except digits
        clean_str = re.sub(r"[^\d]", "", price_str)
        try:
            return int(clean_str)
        except ValueError:
            return None

    def parse(self, url):
        raise NotImplementedError("Subclasses must implement parse()")


class SulpakParser(BaseParser):
    def parse(self, url):
        html = self.get_html(url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, "lxml")
        price_tag = soup.select_one(".product__price") or soup.select_one(".price")
        
        if price_tag:
            return self.clean_price(price_tag.get_text())
        
        return None

class TechnodomParser(BaseParser):
    def parse(self, url):
        html = self.get_html(url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, "lxml")
        # Find the main price container
        container = soup.select_one("div[class*='ProductActions_price__']")
        if not container:
            return None
            
        # Try to find a more specific element inside that might be the current price
        # Often it's a 'p' or 'span' directly under it.
        # We'll try to find the first element that contains only digits and spaces.
        for child in container.find_all(['p', 'span', 'div'], recursive=True):
            text = child.get_text(strip=True)
            digits_only = re.sub(r"[^\d]", "", text)
            if digits_only and len(digits_only) < 10: # Reasonable price length
                return self.clean_price(text)
        
        # Fallback to the whole container's text but only first number group
        text = container.get_text(strip=True)
        # Extract the first group of digits (current price usually comes first)
        match = re.search(r"(\d[\d\s]*)", text)
        if match:
            return self.clean_price(match.group(1))
            
        return None

class AlserParser(BaseParser):
    def parse(self, url):
        html = self.get_html(url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, "lxml")
        
        # Method 1: Try JSON-LD (Search engines see this)
        try:
            scripts = soup.find_all("script", type="application/ld+json")
            for script in scripts:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get("@type") == "Product":
                    offers = data.get("offers")
                    if isinstance(offers, dict):
                        return self.clean_price(str(offers.get("price")))
                    elif isinstance(offers, list) and len(offers) > 0:
                        return self.clean_price(str(offers[0].get("price")))
        except Exception as e:
            logger.error(f"Error parsing JSON-LD for {url}: {e}")

        # Method 2: Fallback to selector
        price_tag = soup.select_one(".price") or soup.select_one(".product-item__price")
        if price_tag:
            return self.clean_price(price_tag.get_text())
        
        return None

class EvrikaParser(BaseParser):
    def parse(self, url):
        html = self.get_html(url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, "lxml")
        # Evrika usually has price in .product-price__current or similar
        price_tag = soup.select_one(".product-price__current") or soup.select_one(".price")
        
        if price_tag:
            return self.clean_price(price_tag.get_text())
        
        return None

class MechtaParser(BaseParser):
    def parse(self, url):
        html = self.get_html(url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, "lxml")
        # Mechta often has price in div[class*='Price_price__']
        price_tag = soup.select_one("div[class*='Price_price__']") or soup.select_one(".price")
        
        if price_tag:
            return self.clean_price(price_tag.get_text())
        
        return None

class KaspiParser(BaseParser):
    def parse(self, url):
        """
        Kaspi has strong anti-bot protection (Cloudflare/Custom).
        Returning None for now as it requires Selenium/Playwright or a specialized API.
        """
        logger.warning(f"Kaspi parsing is not supported via simple requests: {url}")
        return None

def get_parser(marketplace_name):
    parsers = {
        "Sulpak": SulpakParser(),
        "Technodom": TechnodomParser(),
        "Alser": AlserParser(),
        "Evrika": EvrikaParser(),
        "Mechta": MechtaParser(),
        "Kaspi": KaspiParser(),
    }
    return parsers.get(marketplace_name)
