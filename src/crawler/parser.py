"""HTML parsing and link extraction."""

from dataclasses import dataclass, field
from typing import List, Set
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from ..utils.validators import normalize_url
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FormInput:
    """
    Represents an HTML form input field.
    
    Attributes:
        name: Input field name
        type: Input field type (text, password, hidden, etc.)
        value: Default value if present
    """
    
    name: str
    type: str
    value: str = ""


@dataclass
class Form:
    """
    Represents an HTML form.
    
    Attributes:
        action: Form action URL
        method: HTTP method (GET or POST)
        inputs: List of form input fields
    """
    
    action: str
    method: str
    inputs: List[FormInput] = field(default_factory=list)


class Parser:
    """
    HTML parser for extracting links and forms.
    
    Uses BeautifulSoup with lxml parser for fast and robust HTML parsing.
    Handles both relative and absolute URLs, normalizes links for
    duplicate detection.
    """
    
    def __init__(self, base_url: str):
        """
        Initialize parser.
        
        Args:
            base_url: Base URL for resolving relative links
        """
        self.base_url = base_url
    
    def parse_links(self, html: str, current_url: str) -> Set[str]:
        """
        Extract and normalize all links from HTML.
        
        Extracts links from:
        - <a href="...">
        - <link href="...">
        - <script src="...">
        - <img src="...">
        
        Args:
            html: HTML content to parse
            current_url: URL of the current page (for resolving relative links)
        
        Returns:
            Set of normalized absolute URLs
        
        Example:
            >>> parser = Parser("https://example.com")
            >>> links = parser.parse_links("<a href='/page'>Link</a>", "https://example.com")
            >>> print(links)
            {'https://example.com/page'}
        """
        if not html:
            return set()
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            links = set()
            
            # Extract from <a> tags
            for tag in soup.find_all('a', href=True):
                href = tag['href']
                absolute_url = self._make_absolute(href, current_url)
                if absolute_url:
                    links.add(absolute_url)
            
            # Extract from <link> tags (stylesheets, etc.)
            for tag in soup.find_all('link', href=True):
                href = tag['href']
                absolute_url = self._make_absolute(href, current_url)
                if absolute_url:
                    links.add(absolute_url)
            
            # Extract from <script> tags
            for tag in soup.find_all('script', src=True):
                src = tag['src']
                absolute_url = self._make_absolute(src, current_url)
                if absolute_url:
                    links.add(absolute_url)
            
            # Extract from <img> tags
            for tag in soup.find_all('img', src=True):
                src = tag['src']
                absolute_url = self._make_absolute(src, current_url)
                if absolute_url:
                    links.add(absolute_url)
            
            logger.debug(f"Extracted {len(links)} links from {current_url}")
            return links
        
        except Exception as e:
            logger.error(f"Error parsing HTML from {current_url}: {e}")
            return set()
    
    def parse_forms(self, html: str, current_url: str) -> List[Form]:
        """
        Extract form elements with attributes and inputs.
        
        Args:
            html: HTML content to parse
            current_url: URL of the current page
        
        Returns:
            List of Form objects
        
        Example:
            >>> parser = Parser("https://example.com")
            >>> forms = parser.parse_forms(html, "https://example.com/page")
            >>> for form in forms:
            ...     print(f"{form.method} {form.action}")
        """
        if not html:
            return []
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            forms = []
            
            for form_tag in soup.find_all('form'):
                # Get form attributes
                action = form_tag.get('action', '')
                method = form_tag.get('method', 'GET').upper()
                
                # Make action URL absolute
                if action:
                    action = self._make_absolute(action, current_url) or action
                else:
                    action = current_url
                
                # Extract input fields
                inputs = []
                for input_tag in form_tag.find_all(['input', 'textarea', 'select']):
                    name = input_tag.get('name', '')
                    if not name:
                        continue
                    
                    input_type = input_tag.get('type', 'text')
                    value = input_tag.get('value', '')
                    
                    inputs.append(FormInput(
                        name=name,
                        type=input_type,
                        value=value
                    ))
                
                forms.append(Form(
                    action=action,
                    method=method,
                    inputs=inputs
                ))
            
            logger.debug(f"Extracted {len(forms)} forms from {current_url}")
            return forms
        
        except Exception as e:
            logger.error(f"Error parsing forms from {current_url}: {e}")
            return []
    
    def _make_absolute(self, url: str, base: str) -> str:
        """
        Convert relative URL to absolute and normalize.
        
        Args:
            url: URL to convert (may be relative or absolute)
            base: Base URL for resolving relative URLs
        
        Returns:
            Normalized absolute URL or empty string if invalid
        """
        try:
            # Skip non-HTTP(S) URLs
            if url.startswith(('javascript:', 'mailto:', 'tel:', 'data:', '#')):
                return ""
            
            # Make absolute
            absolute = urljoin(base, url)
            
            # Validate scheme
            parsed = urlparse(absolute)
            if parsed.scheme not in ['http', 'https']:
                return ""
            
            # Normalize
            normalized = normalize_url(absolute)
            return normalized
        
        except Exception as e:
            logger.debug(f"Error making URL absolute: {url} - {e}")
            return ""
