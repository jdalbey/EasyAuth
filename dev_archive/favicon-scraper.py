import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import List, Dict
import logging
from dataclasses import dataclass
import mimetypes
"""REF: https://claude.ai/chat/21568668-db6c-4a9b-9f5a-cfaf034704b1"""
@dataclass
class FaviconInfo:
    """Data class to store favicon metadata"""
    url: str
    size: tuple[int, int] | None
    type: str | None
    rel: str | None

class FaviconScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.logger = logging.getLogger(__name__)

    def _parse_size(self, sizes: str | None) -> tuple[int, int] | None:
        """Parse size string (e.g., '16x16' or '32x32') into tuple."""
        if not sizes:
            return None
        
        match = re.match(r'(\d+)x(\d+)', sizes)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        return None

    def _guess_mimetype(self, url: str) -> str | None:
        """Guess mimetype from URL extension."""
        ext = urlparse(url).path.split('.')[-1].lower()
        return mimetypes.guess_type(f"file.{ext}")[0]

    def _normalize_url(self, base_url: str, favicon_url: str) -> str:
        """Convert relative URLs to absolute URLs."""
        if not favicon_url:
            return None
        
        # Handle data URIs
        if favicon_url.startswith('data:'):
            return favicon_url
            
        # Handle protocol-relative URLs
        if favicon_url.startswith('//'):
            parsed_base = urlparse(base_url)
            return f"{parsed_base.scheme}:{favicon_url}"
            
        return urljoin(base_url, favicon_url)

    def get_favicons(self, url: str) -> List[FaviconInfo]:
        """
        Scrape favicon information from a website.
        
        Args:
            url: The website URL to scrape
            
        Returns:
            List of FaviconInfo objects containing favicon metadata
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            favicons = []
            
            # Check for link tags
            for link in soup.find_all('link'):
                rel = link.get('rel', [])
                if isinstance(rel, str):
                    rel = [rel]
                    
                if any(r.lower() in ['icon', 'shortcut icon', 'apple-touch-icon', 'mask-icon'] for r in rel):
                    favicon_url = self._normalize_url(url, link.get('href'))
                    if not favicon_url:
                        continue
                        
                    favicon = FaviconInfo(
                        url=favicon_url,
                        size=self._parse_size(link.get('sizes')),
                        type=link.get('type') or self._guess_mimetype(favicon_url),
                        rel=', '.join(rel)
                    )
                    favicons.append(favicon)
            
            # Check for default favicon.ico if none found
            if not favicons:
                default_favicon = urljoin(url, '/favicon.ico')
                try:
                    resp = self.session.head(default_favicon)
                    if resp.status_code == 200:
                        favicons.append(FaviconInfo(
                            url=default_favicon,
                            size=None,
                            type='image/x-icon',
                            rel='icon'
                        ))
                except requests.RequestException:
                    pass
            
            return favicons
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return []

    def get_favicon_details(self, url: str) -> List[Dict]:
        """
        Get favicon details in dictionary format for easier processing.
        
        Args:
            url: The website URL to scrape
            
        Returns:
            List of dictionaries containing favicon metadata
        """
        favicons = self.get_favicons(url)
        return [
            {
                'url': f.url,
                'size': f'{f.size[0]}x{f.size[1]}' if f.size else None,
                'type': f.type,
                'rel': f.rel
            }
            for f in favicons
        ]

# Example usage
if __name__ == '__main__':
    scraper = FaviconScraper()
    url = "https://www.figma.com"
    favicons = scraper.get_favicon_details(url)
    
    for favicon in favicons:
        print("\nFavicon found:")
        for key, value in favicon.items():
            print(f"{key}: {value}")
