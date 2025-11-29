import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse

def start_crawling(url,prefix,depth):
    visited_urls=set()
    wanted_urls=set()

    def crawl_urls(url,prefix,depth):
        if depth<0:
            return
        visited_urls.add(url)
        try:
            response=requests.get(url)
            soup=BeautifulSoup(response.content,"html.parser")
            print(f"Crawling: {url}")
            for anchor in soup.find_all("a"):
                href=anchor.get("href")
                if href:
                    absoulte_url=urljoin(url,href)
                    print(f"Found URL: {absoulte_url}")
                    if absoulte_url.startswith(prefix):
                        parsed_url = urlparse(absoulte_url)
                        if not parsed_url.fragment:
                            wanted_urls.add(absoulte_url) 
                    if absoulte_url not in visited_urls:
                        crawl_urls(absoulte_url,prefix,depth-1)
        except requests.exceptions.RequestException as e:
            print(f"Error crawling {url}: {e}")
    crawl_urls(url,prefix,depth)
    return list(sorted(wanted_urls))  