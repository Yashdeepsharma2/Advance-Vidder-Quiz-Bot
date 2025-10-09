# Powered by Viddertech

import logging
import requests
from bs4 import BeautifulSoup, NavigableString

logger = logging.getLogger(__name__)

class WebScraper:
    """
    A class to handle scraping article text from web pages.
    """

    @staticmethod
    def scrape_article_text(url: str) -> str:
        """
        Fetches a URL and extracts the main article text using heuristics.

        :param url: The URL of the article to scrape.
        :return: The cleaned article text.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() # Raise an exception for bad status codes

            soup = BeautifulSoup(response.content, 'html.parser')

            # --- Common Scraping Heuristics ---
            # Remove common non-content tags
            for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form']):
                tag.decompose()

            # Find the main content. This often works for articles.
            main_content = soup.find('article') or soup.find('main') or soup.find('body')

            if not main_content:
                raise Exception("Could not find main content of the page.")

            # Get all text, trying to preserve some structure with paragraph breaks
            text_parts = []
            for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'li']):
                text = element.get_text(separator=' ', strip=True)
                if text:
                    text_parts.append(text)

            cleaned_text = "\n\n".join(text_parts)

            if not cleaned_text:
                # Fallback if the tag-based approach fails
                cleaned_text = main_content.get_text(separator='\n', strip=True)

            logger.info(f"Successfully scraped text from URL: {url}")
            return cleaned_text

        except requests.RequestException as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            raise Exception(f"Could not connect to the URL: {e}")
        except Exception as e:
            logger.error(f"Failed to scrape article from {url}: {e}")
            raise # Re-raise the exception to be handled by the command handler