import json
import requests
from pprint import pprint
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import WriteError, BulkWriteError


password = '9K3G4xwyH57qP8Nh'
client = MongoClient(
    f"mongodb+srv://vovchik357:{password}@cluster0.imbqfnj.mongodb.net/Cluster0?retryWrites=true&w=majority",
    server_api=ServerApi('1')
)
db = client.quotes_and_authors


def create_db():
    '''Creating collections'''
    db.create_collection("quotes")
    db.create_collection("authors")


url = 'https://quotes.toscrape.com'


def parse_author(link):
    '''Find info about author'''
    author = {}
    response = requests.get(url + link)
    soup = BeautifulSoup(response.text, 'lxml')
    fullname = soup.find('h3', class_='author-title')
    born_date = soup.find('span', class_='author-born-date')
    born_location = soup.find('span', class_='author-born-location')
    description = soup.find('div', class_='author-description')

    author['fullname'] = fullname.text
    author['born_date'] = born_date.text
    author['born_location'] = born_location.text
    author['description'] = description.text.strip()

    return author


quotes_list, authors_list = [], []


def parse(link):
    '''Find quotes and links to author about and next page'''
    response = requests.get(url + link)
    soup = BeautifulSoup(response.text, 'lxml')
    quotes = soup.find_all('span', class_='text')
    authors = soup.find_all('small', class_='author')
    tags = soup.find_all('div', class_='tags')

    for i, quote in enumerate(quotes):
        quotes_dict = {}
        quotes_dict["quote"] = quote.text
        quotes_dict["author"] = authors[i].text
        tags_for_quote = tags[i].find_all('a', class_='tag')
        tags_list = [tag.text for tag in tags_for_quote]
        quotes_dict["tags"] = tags_list
        quotes_list.append(quotes_dict)

    hrefs = soup.select("[href^='/author/']")
    for href in hrefs:
        authors_list.append(parse_author(href["href"]))

    next_button = soup.find('li', class_='next')
    if next_button:
        next_link = next_button.find('a')["href"]
        parse(next_link)


def save_to_json(filename, data):
    '''Dump data to json'''
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def save_json_to_db(filename, db_name):
    '''Open json and insert data to database'''
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    try:
        result = db_name.insert_many(data)
        return result.inserted_ids
    except (WriteError, BulkWriteError) as e:
        print(e)


if __name__ == '__main__':
    print('Start')
    # create_db()
    # parse('/')
    # pprint(quotes_list)
    # pprint(authors_list)
    # save_to_json('quotes.json', quotes_list)
    # save_to_json('authors.json', authors_list)
    # pprint(save_json_to_db('quotes.json', db.quotes))
    # pprint(save_json_to_db('authors.json', db.authors))
    # db.quotes.delete_many({})
    # db.authors.delete_many({})
