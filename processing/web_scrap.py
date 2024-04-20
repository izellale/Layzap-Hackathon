import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

import os


URL = "https://www.vd.ch/population/population-etrangere/entree-et-sejour/transformation-de-lautorisation-de-sejour-b-en-autorisation-detablissement-c"
r = requests.get(URL)
soup = BeautifulSoup(r.content, 'html.parser')



paragraphs = soup.find(class_="container mt-5 vd-content")
with open(URL.split('/')[-1], 'w', encoding='utf-8') as file:
    file.write(paragraphs.get_text(strip=True))


links = soup.find_all('a')
valid = []
for link in links:
    url = link.get('href')
    if url:
        if url.startswith('/'):
            valid.append('https://www.vd.ch' + url)


def fetch_and_extract_text(url):
    try:
        # Send the request
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        # Parse the page
        page_soup = BeautifulSoup(response.text, 'html.parser')
        page_content = page_soup.find(class_="container mt-5 vd-content")
        # Extract text
        if page_content:
            return page_content.get_text(strip=True)
        else:
            return None
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


for link in tqdm(valid, total=len(valid)):
    text = fetch_and_extract_text(link)
    if text:
        if link.split('/')[-1] != '':
            with open(link.split('/')[-1], 'w', encoding='utf-8') as file:
                file.write(text)
