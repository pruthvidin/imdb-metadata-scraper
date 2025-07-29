import requests
from bs4 import BeautifulSoup 

def search_imdb(title):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    try:
        search_url = f"https://www.imdb.com/find?q={requests.utils.quote(title)}&s=tt&ttype=ft,tv&ref_=fn_ft"
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        first_result = soup.select_one('li.ipc-metadata-list-summary-item a.ipc-metadata-list-summary-item__t')
        if not first_result:
            return None

        title_text = first_result.text.strip()
        year_span = first_result.find_next('span', class_='dli-title-metadata-item')
        year = year_span.text.strip() if year_span else 'N/A'
        url = 'https://www.imdb.com' + first_result['href'].split('?')[0]

        return {
            'title': title_text,
            'year': year,
            'url': url
        }

    except Exception as e:
        print(f"Error searching IMDb: {e}")
        return None

def scrape_imdb(title_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    try:
        response = requests.get(title_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        metadata = {
            'title': None,
            'year': None,
            'rating': None,
            'genres': [],
            'duration': None,
            'directors': [],
            'cast': [],
            'plot': None
        }

        # Title
        title_element = soup.select_one('h1[data-testid="hero__pageTitle"] span') or soup.select_one('h1.sc-afe43def-1 span')
        if title_element:
            metadata['title'] = title_element.text.strip()

        # Year
        year_element = soup.select_one('a[href*="releaseinfo"]')
        if year_element:
            metadata['year'] = year_element.text.strip()

        # Rating
        rating_element = soup.select_one('span.sc-bde20123-1') or soup.select_one('div[data-testid="hero-rating-bar__aggregate-rating__score"] span')
        if rating_element:
            metadata['rating'] = rating_element.text.strip()

        # Genres
        genre_container = soup.select('div[data-testid="genres"] a.ipc-chip--on-baseAlt') or soup.select('div.ipc-chip-list a.ipc-chip--on-baseAlt')
        metadata['genres'] = [genre.text.strip() for genre in genre_container]

        # Duration
        duration_element = soup.select_one('li[data-testid="title-techspec_runtime"]')
        if duration_element:
            metadata['duration'] = duration_element.get_text(' ', strip=True).replace('Runtime', '').strip()

        # Director
        director_section = soup.find('div', class_='ipc-metadata-list-item__content-container')
        if director_section and ('Director' in director_section.get_text() or 'Directors' in director_section.get_text()):
            directors = director_section.find_all('a', href=lambda x: x and '/name/' in x)
            metadata['directors'] = [d.text.strip() for d in directors]


        if not metadata['directors']:
            for section in soup.select('li.ipc-metadata-list__item'):
                if 'Director' in section.get_text() or 'Directors' in section.get_text():
                    directors = section.find_all('a', href=lambda x: x and '/name/' in x)
                    metadata['directors'] = [d.text.strip() for d in directors]
                    break

        if not metadata['directors']:
            director_link = soup.find('a', {'data-testid': 'title-pc-principal-credit'})
            if director_link and 'Director' in director_link.parent.get_text():
                metadata['directors'] = [director_link.text.strip()]

        # Top 5 Cast Members
        cast_section = soup.select('div[data-testid="title-cast-item"]') or soup.select('table.cast_list tr')[1:6]
        for item in cast_section[:5]:
            actor = item.select_one('a[data-testid="title-cast-item__actor"]') or item.select_one('td:not([class]) a')
            if actor:
                metadata['cast'].append(actor.text.strip())

        # Plot
        plot_element = soup.select_one('span[data-testid="plot-xl"]') or soup.select_one('div.summary_text')
        if plot_element:
            metadata['plot'] = plot_element.get_text(strip=True)

        return metadata

    except Exception as e:
        print(f"Error scraping IMDb: {e}")
        return None

def display_metadata(metadata):
    """Display the collected metadata in a readable format"""
    print("\n=== Metadata ===")
    print(f"Title: {metadata.get('title', 'N/A')}")
    print(f"Year: {metadata.get('year', 'N/A')}")
    print(f"Rating: {metadata.get('rating', 'N/A')}")
    print(f"Genres: {', '.join(metadata.get('genres', ['N/A']))}")
    print(f"Duration: {metadata.get('duration', 'N/A')}")
    print(f"Directors: {', '.join(metadata.get('directors', ['N/A']))}")
    print(f"Top Cast: {', '.join(metadata.get('cast', ['N/A']))}")
    print(f"Plot: {metadata.get('plot', 'N/A')}")


print("IMDb Movie Metadata Scraper")
print("-----------------------------------")

search_query = input("\nEnter a movie: ").strip()
if not search_query:
    print("Please enter a valid name.")

print(f"\nSearching IMDb for '{search_query}'...")
search_result = search_imdb(search_query)

if not search_result:
    print("No results found. Please try another search.")


print(f"\nFetching details for {search_result['title']}...")
metadata = scrape_imdb(search_result['url'])

if metadata:
    display_metadata(metadata)
else:
    print("Failed to fetch details.")
