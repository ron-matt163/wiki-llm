import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_text_from_url(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "noscript", "meta", "header", "footer", "nav"]):
            tag.extract()

        text = soup.get_text(separator=" ")
        text = " ".join(text.split())

        return text

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def fetch_wikipedia_html(search_keyword, lang="en"):
    """
    Fetches Wikipedia page content in HTML format using the MediaWiki API.

    :param search_keyword: The title of the Wikipedia page.
    :param lang: Wikipedia language (default is English).
    :return: HTML content as a string or None if the page is not found.
    """
    url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "parse",
        "page": search_keyword,
        "format": "json",
        "prop": "text",
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "error" in data:
        print(f"Error: {data['error']['info']}")
        return None

    return data["parse"]["text"]["*"]  # Wikipedia page HTML content

def extract_text_and_tables(wikipedia_html):
    """
    Extracts clean text and only valid tables from Wikipedia HTML content using BeautifulSoup.

    :param wikipedia_html: The HTML content of a Wikipedia page.
    :return: A tuple (cleaned_text, tables_list).
    """
    soup = BeautifulSoup(wikipedia_html, "html.parser")

    for tag in soup(["script", "style", "noscript", "meta", "header", "footer", "nav", "aside"]):
        tag.extract()

    paragraphs = soup.find_all("p")
    clean_text = "\n".join(p.get_text() for p in paragraphs if p.get_text().strip())

    tables = []
    for i, table in enumerate(soup.find_all("table", class_="wikitable")):  
        # **Filter only structured Wikipedia tables** 
        if not table.find("th"):  # Skip if no headers (avoid misinterpreted tables)
            continue

        try:
            df = pd.read_html(str(table), flavor="bs4")[0]
            if len(df) > 1:  # Ensure the table has more than just headers
                tables.append(df)
        except ValueError:
            print(f"Skipping table {i}: Could not parse.")

    return clean_text, tables

def scrape_wikipedia_page(search_keyword):
    """
    Scrapes Wikipedia page text and tables for a given search keyword.

    :param search_keyword: Wikipedia page title.
    :return: None (prints extracted content and tables).
    """
    wikipedia_html = fetch_wikipedia_html(search_keyword)

    if not wikipedia_html:
        print("No content retrieved.")
        return

    return extract_text_and_tables(wikipedia_html)


if __name__ == "__main__":
    url = "https://rubrik.com/"
    scraped_text = scrape_text_from_url(url)

    if scraped_text:
        print(scraped_text[:1000])

    search_term = "Erling Haaland"  # Wikipedia page title
    clean_text, tables =  scrape_wikipedia_page(search_term)
    print("\nExtracted Text (Preview):\n", clean_text[:1000], "...\n")

    if tables:
        for i, table in enumerate(tables):
            print(f"\nTable {i + 1}:\n", table)
    else:
        print("\nNo tables found on this Wikipedia page.")