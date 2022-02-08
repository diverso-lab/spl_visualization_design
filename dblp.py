from re import search
import requests
import json
import argparse
from bs4 import BeautifulSoup


USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
HEADERS = {'User-Agent': USER_AGENT}
AUTHOR = 'José Miguel Horcas'
URL_VENUE_QUERIES = 'https://dblp.org/search/venue/api'
DOI_URL = 'https://doi.org/'


"""
https://dblp.org/faq/13501473.html
"""


def search_venue(query: str, max_results: int=1000, page: int=0) -> dict[str, str]:
    """Search for the URL of a venue in DBLP.
    
    Return a dictionary of venues's names and URLs matching with the query.
    """
    url = f'{URL_VENUE_QUERIES}?q={query}&format=json&h={max_results}&f={page}'
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        print('Error "search_venue". Status code: ' + str(r.status_code))
        return []

    data = r.json()
    #print(json.dumps(data, indent=2, sort_keys=True))
    hits = data['result']['hits']
    n_results = int(hits['@sent'])
    if n_results == 0:
        return {}

    # Extract venue's name and id (url)
    venues = {}
    for hit in hits['hit']:
        name = hit['info']['venue']
        url = hit['info']['url']
        venues[name] = url

    # Pagination
    if n_results == max_results:
        next_venues = search_venue(query, max_results, page+max_results)
        venues.update(next_venues)

    return venues


def get_pubs(query: str, max_results: int=1000, page: int=0) -> list:
    url = 'http://dblp.org/search/publ/api?q=author:' + query + ':&format=json&h=' + str(max_results) + '&f=' + str(page)
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        print('Error "get_pubs". Status code: ' + str(r.status_code))
        return []

    data = r.json()
    print(json.dumps(data, indent=2, sort_keys=True))


# def search_author(query: str, max_results: int=1000, page: int=0) -> list:
#     """Search for authors in DBLP.

#     Returns:
#         A list of tuples with the complete author's name and url.
#         Example for query 'Horcas':
#             [('Esperanza Horcas', 'https://dblp.org/pid/219/4858'),
#              ('Ignacio Horcas', 'https://dblp.org/pid/167/1749'),
#              ('Jose Miguel Horcas', 'https://dblp.org/pid/142/9275')]

#     """
#     url = 'http://dblp.org/search/author/api?q=' + query + '&format=json&h=' + str(max_results) + '&f=' + str(page)
#     r = requests.get(url)
#     if r.status_code != requests.codes.ok:
#         print('Error "search_autor". Status code: ' + str(r.status_code))
#         return []

#     data = r.json()
#     print(json.dumps(data, indent=2, sort_keys=True))
#     hits = data['result']['hits']
#     n_results = int(hits['@sent'])
#     if n_results == 0:
#         return []

#     # Extract author's name and id (url)
#     authors = []
#     for hit in hits['hit']:
#         author = hit['info']['author']
#         author_url = hit['info']['url']
#         authors.append((author,author_url))

#     # Pagination
#     if n_results == max_results:
#         next_authors = search_author(query, max_results, page+max_results)
#         authors += next_authors

#     return authors


def extract_doi_publications_from_venue_url(url: str) -> list[str]:
    """Extract all the publications with a DOI from a particular venue URL."""
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')
 
    urls = set()
    for link in soup.find_all('a'):
        href = link.get('href')
        if href is not None and href.startswith(DOI_URL):
            urls.add(href)
    return list(urls)
 
def count_publications_from_venue_url(url: str) -> int:
    """Count the number of publications in a venue URL"""
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')
 
    count = 0
    for link in soup.find_all('img'):
        href = link.get('title')
        if href is not None and href == 'Conference and Workshop Papers':
            count += 1
    return count 

def extract_venue_urls(url: str) -> list[str]:
    """Extract all the URL for a particular venue URL."""
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')
 
    urls = set()
    for link in soup.find_all('a'):
        href = link.get('href')
        if href is not None and href.startswith(url):
            urls.add(href)
    return list(urls)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""DBLP search API."""
    )

    parser.add_argument('-v', '--venue', help='Search for a venue', dest='venue', required=False)
    args = parser.parse_args()

    if args.venue:
        print(f'Searching for venue "{args.venue}"...')  
        venues = search_venue(args.venue)
        if venues:
            print('Results:')
            for i, (venue, url) in enumerate(venues.items(), 1):
                print(f'{i}: {venue} -> {url}')
        else:
            print(f'No results for venue "{args.venue}".')
        
        if len(venues) > 1:
            print('Too many results, please use a more specific identifier to query for the venue.')
        elif len(venues) == 1:
            venue, url = next(iter(venues.items()))
            urls = extract_venue_urls(url)
            for u in sorted(urls):
                nof_papers = count_publications_from_venue_url(u)
                print(f'{u} -> {nof_papers}')
                #for p in papers:
                    
