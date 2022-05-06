from urllib.parse import urlparse

from ..base import BaseShortener
from ..exceptions import (
    ShorteningErrorException,
    ExpandingErrorException,
    BadURLException,
)


class Shortener(BaseShortener):
    """Short.cm shortener Implementation

    Args:
        api_key (str): short.cm API key

    Example:

        >>> import pyshortener
        >>> s = pyshortener.Shortener(api_key='YOUR_KEY')
        >>> s.shortcm.short('http://www.google.com')
        'http://short.cm/TEST'
        >>> s.shortcm.expand('https://short.cm/test')
        'http://www.google.com'
        >>> s.shortcm.expand('https://short.cm/test')
        10
    """

    api_url = "https://api.short.cm/links/"
    domain_url = "https://api.short.cm/api/domains"
    api_key = ""

    def short(self, url):
        """Short implementation for Short.cm
        Args:
            url (str): the URL you want to shorten

        Returns:
            str: The shortened URL

        Raises:
            BadAPIResponseException: If the data is malformed or we got a bad
            status code on API response
            ShorteningErrorException: If the API Returns an error as response
        """

        self.clean_url(url)
        headers = {"authorization": self.api_key}
        response_= self._get(self.domain_url,headers=headers)
        domain = response_.json()[0]['hostname']
        json = {"originalURL": url, "domain": domain}
        response = self._post(self.api_url, json=json, headers=headers)
        if response.ok:
            data = response.json()
            if "shortURL" not in data:
                raise ShorteningErrorException(
                    f"API Returned wrong response: " f"{data}"
                )
            return data["shortURL"]
        raise ShorteningErrorException(response.content)

    def expand(self, url):
        """Expand implementation for Short.cm
        Args:
            url: the short URL you want to expand

        Returns:
            str: The expanded URL

        Raises:
            ExpandingErrorException: If the API Returns an error as response
        """
        expand_url = f"{self.api_url}expand"

        cleaned_url = self.clean_url(url)

        # split domain and path
        url_parsed = urlparse(cleaned_url)

        if url_parsed.hostname is None:
            raise BadURLException(f"{cleaned_url}")

        params = {"domain": url_parsed.hostname, "path": url_parsed.path.strip("/")}
        headers = {"authorization": self.api_key}
        response = self._get(expand_url, params=params, headers=headers)
        if response.ok:
            data = response.json()
            if "originalURL" not in data:
                raise ShorteningErrorException(
                    f"API Returned wrong response: " f"{data}"
                )
            return data["originalURL"]
        raise ExpandingErrorException(response.content)
