import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

class Spine:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_quotes(self):
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, 'lxml')
        return soup.find_all('div', class_='quote')

    def get_quote_data(self, quote: BeautifulSoup):
        return {
            'text': quote.find('span', class_='text').text,
            'author': quote.find('small', class_='author').text,
            'tags': [tag.text for tag in quote.find_all('a', class_='tag')]
        }

    def get_authors_links(self, quotes: list[BeautifulSoup]):
        return [quote.find_all('span')[1].find('a')['href'] for quote in quotes]


class Connection:
    def __init__(self, client: MongoClient, db_name: str, collection_name: str):
        self.db = client[db_name]
        self.collection = self.db[collection_name]

    def add(self, quotes: list[dict]):
        self.collection.insert_many(quotes)

class AuthorSpine:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_author_data(self, author_link: str):
        response = requests.get(self.base_url + author_link)
        return  BeautifulSoup(response.text, 'lxml')

    def get_author_info(self, author_data: BeautifulSoup):
        return {
            'name': author_data.find('h3', class_='author-title').text,
            'born_date': author_data.find('span', class_='author-born-date').text,
            'born_location': author_data.find('span', class_='author-born-location').text,
            'description': author_data.find('div', class_='author-description').text.replace('\n', '').strip()
        }

if __name__ == "__main__":
    spine = Spine('http://quotes.toscrape.com/')
    quotes = spine.get_quotes()

    # get quotes
    quotes_list = [spine.get_quote_data(quote) for quote in quotes]

    with MongoClient("mongodb://admin:secret@localhost:27017") as client:
        connection = Connection(client, 'quotes', 'quotes')
        connection.add(quotes_list)

    # get authors
    authors_links = spine.get_authors_links(quotes)
    authors_info = []
    for link in authors_links:
        autor_spine = AuthorSpine(spine.base_url)
        autor_data = autor_spine.get_author_data(link)
        autor_info = autor_spine.get_author_info(autor_data)
        authors_info.append(autor_info)

    with MongoClient("mongodb://admin:secret@localhost:27017") as client:
        connection = Connection(client, 'authors', 'authors')
        connection.add(authors_info)
