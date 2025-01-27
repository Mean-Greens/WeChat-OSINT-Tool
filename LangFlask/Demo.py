# Need documentation for this file

# This file contains a hardcoded cookies which are required to bypass Sogou bot detection.
# We will attempt automatic creation/retrieval of this cookie later.
#
import datetime
import httpx
import re
import time
import unicodedata
from bs4 import BeautifulSoup
import os
import ollama
import chromadb
from MGHTMLLoader import MGHTMLLoader
from typing import Dict, Iterator, Union
from langchain_core.documents import Document
from get_vector_db import get_vector_db, get_chunked_db
from query import query
from langchain_text_splitters import RecursiveCharacterTextSplitter
import hashlib
import random
import logging
from rich.traceback import install
from pathlib import Path
from collections import OrderedDict

install(show_locals=True)

# Creates a log file for the Wechat web
log_file_path = os.path.join(os.path.dirname(__file__), 'Wechat_Scraper.log')
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    encoding="utf-8",
    format='{asctime} - {levelname} - {message}',
    style="{"
)

'''
pip install httpx beautifulsoup4 ollama chromadb
'''

HEADERS = {
            'Host': 'weixin.sogou.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'DNT': '1',
            'Sec-GPC': '1',
            'Connection': 'keep-alive',
            'Referer': 'https://weixin.sogou.com/',
            'Cookie': 'IPLOC=NL; SUID=8CFD08D41AA7A20B000000006781FE67; cuid=AAHKs2cKUQAAAAuipsd9DwIA4wQ=; SUV=1736572520882172; ABTEST=0|1736572526|v1; SNUID=3F49BB67B4B59FD3FF27C4B3B4094BC1; ariaDefaultTheme=undefined',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-User': '?1',
            'Priority': 'u=0, i'
        }


BASE_URL_1 = 'https://weixin.sogou.com/weixin?type=2&s_from=input&query=' # query in chinese
BASE_URL_2 = '&ie=utf8'

QUESTION = '哪种香蕉布丁最好吃？' # Which banana pudding is best?
SEARCH_TERM = '香蕉布丁' # Banana pudding

FORCE_WORDLIST_RESTART = False

# Get the directory path of the current file
#current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the 'db' folder to the directory path
#db_path = os.path.join(current_dir, 'db')

#client = chromadb.PersistentClient(path=db_path)

#collection = client.get_or_create_collection(name="demo")

# Timer decorator
def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        # Calculate the elapsed time
        elapsed_time = end_time - start_time

        # Convert the elapsed time to hours, minutes, and seconds
        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)

        elapsed_time = f"--- {int(hours)} hours, {int(minutes)} minutes, {seconds:.2f} seconds ---"
        print(elapsed_time)
        logging.info(elapsed_time)
        return result
    return wrapper

def read_search_terms():
    with open('Wordlist.txt', 'r', encoding='utf-8') as f:
        search_terms = f.readlines()
        for i, term in enumerate(search_terms):
            search_terms[i] = term.strip()
        search_terms = list(filter(None, search_terms))
        unique_search_terms = list(OrderedDict.fromkeys(search_terms))
    return unique_search_terms

def timeConvert(unix_timestamp): 
    # Convert the Unix timestamp to a datetime object 
    dt = datetime.datetime.fromtimestamp(int(unix_timestamp)) 
    # Format the datetime object as a string 
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def get_html(url, retries=5, wait_time=120):
    with httpx.Client() as client:
        attempt = 0
        while attempt < retries:
            try:
                response = client.get(url, headers=HEADERS, follow_redirects=True, timeout=60.0)
                # response.raise_for_status() # Raise an exception for HTTP errors
                break
            except httpx.ReadTimeout:
                print(f"ReadTimeout occured, retrying in {wait_time} seconds...")
                logging.warning(f"ReadTimeout occured, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                attempt += 1
        if attempt == retries:
            logging.critical(f"failed to fetch the URL after {retries} attempts -- line 120")
            raise Exception(f"failed to fetch the URL after {retries} attempts -- line 121")

        if response.status_code != 200:
            print(f"Non-200 response: {url} - Status Code: {response.status_code}")
            logging.error(f"Non-200 response: {url} - Status Code: {response.status_code}")
        
        return BeautifulSoup(response.text, 'html.parser')
    
def get_wechat_link(url):
    with httpx.Client() as client:
        
        response = client.get(url, headers=HEADERS)
        if response.status_code == 302:
            print(response.headers) 
            print("You have been blocked")
            logging.error(response.headers)
            logging.error("You have been blocked")
            return None
        elif response.status_code == 200:
            WCUrl = ""
            pattern = r"url \+= '(.*?)';"
            matches = re.findall(pattern, response.text)
            for match in matches:
                WCUrl += match

            return WCUrl   
        else:
            print(response.status_code)
            print("Failed to retrieve the website")
            logging.error(response.status_code)
            logging.error("Failed to retrieve the website")
            return None
        
def read_website(url, retries=5, wait_time=120):
    """
    Reads and returns the body of the website at the given url.
    Args:
        url (str): The url of the website to read.
    Returns:
        str: The body of the website.
        None: If the request fails.
    """
    with httpx.Client() as client:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0'}

        attempt = 0
        while attempt < retries:
            try:
                response = client.get(url, headers=headers, follow_redirects=True, timeout=60.0)
                # response.raise_for_status() # Raise an exception for HTTP errors
                break
            except httpx.ReadTimeout:
                print(f"ReadTimeout occured, retrying in {wait_time} seconds...")
                logging.warning(f"ReadTimeout occured, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                attempt += 1
        if attempt == retries:
            logging.critical(f"failed to fetch the URL after {retries} attempts -- line 178")
            raise Exception(f"failed to fetch the URL after {retries} attempts -- line 179")

        if response.status_code == 200:
            website = response.content

            soup = BeautifulSoup(response.text, 'html.parser')
            body = soup.body
            body_text = body.get_text(strip=True)
            normalized_text = unicodedata.normalize("NFKD", body_text)
            normalized_text = ' '.join(normalized_text.split())
            return normalized_text, website
        else:
            print(response.status_code)
            print("Failed to retrieve the website")
            logging.error(response.status_code)
            logging.error("Failed to retrieve the website")
            return None
   
def sogou_searcher(query):

    documents = []
    print(query)
    logging.info(query)
    html = get_html(f'{BASE_URL_1}{query}{BASE_URL_2}')

    try:
        body = html.find('body')
        links_wrapper = body.find(id='wrapper')
        links_main = links_wrapper.find(id='main')
        news_box = links_main.find('div', class_='news-box')
        news_list = news_box.find('ul')
        news_sites = news_list.find_all('li')
    except:
        print("No search results were returned")
        logging.warning("No search results were returned")
        return documents
    
    for site in news_sites:
        link_box = site.find(class_='txt-box')
        title = link_box.find('h3').text.strip()
        description = link_box.find('p', class_='txt-info').text.strip()
        data = link_box.find('div', class_='s-p')
        author = data.find('span', class_='all-time-y2').text.strip()
        date = data.find('span', class_='s2').find('script').text.strip()

        pattern = r'document.write\(timeConvert\(\'(\d+)\'\)\)'
        match = re.match(pattern, date)
        if match:
            date = match.group(1)

        link_tag = link_box.find('a', href=True)
        link = "https://weixin.sogou.com" + link_tag.get('href')

        link = get_wechat_link(link)
        if link == None:
            continue
        normalized_text, website = read_website(link)
        if website == None:
            continue
        web_hash = hashlib.sha256(normalized_text.encode('utf-8')).hexdigest()
        # web_hash = hashlib.sha256(normalized_text).hexdigest()
        metadata: Dict[str, Union[str, None]] = {
            "source": link,
            "title": title,
            "description": description,
            "author": author,
            "date": date,
            "hash": web_hash
        }

    
        doc = [Document(page_content=website, metadata=metadata), Document(page_content = normalized_text, metadata=metadata)]
        
        documents.append(doc)

    return documents

def store_websites(documents:list):
    # store each document in a vector embedding database
    db = get_vector_db()

    # Chunk documents and store in a seperate collection that the LLM will use
    db_chunked = get_chunked_db()

    for doc in documents:
        
        if document_exists_by_hash(db, doc[0].metadata.get("hash")):
            print("Document already exists")
            logging.info("Document already exists")
        else:
            print("Adding document to DB")
            logging.info("Adding document to DB")

            # Save space by only saving the metadata in the database and not the articles
            db.add_documents([Document(page_content=' ', metadata=doc[0].metadata)])

            chunk_doc = doc[1]
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
            chunks = text_splitter.split_documents([chunk_doc])
            db_chunked.add_documents(chunks)

            # Save the HTML file to an Articles folder on the desktop
            Path(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), f'Articles/{doc[0].metadata.get("hash")}.html')).write_text(doc[0].page_content)

def document_exists_by_hash(vectorstore, hash_value):
    results = vectorstore.similarity_search_with_score(
        query="",
        k=1,
        filter={"hash": hash_value}
    )
    return bool(results)

@timer
def main(search_term):
    documents = sogou_searcher(search_term)
    store_websites(documents)

def scrape():
    global FORCE_WORDLIST_RESTART
    while True:
            # This refreshes the wordlist after all terms are scraped
            queries = read_search_terms()

            for query in reversed(queries):
                if FORCE_WORDLIST_RESTART:
                    FORCE_WORDLIST_RESTART = False
                    break

                main(query)

                # Generate a random time between 4 and 6 minutes (in seconds)
                random_sleep_time = random.uniform(15 * 60, 20 * 60)
                
                # Sleep for the random time
                time.sleep(random_sleep_time)
                print(f"Slept for {random_sleep_time / 60:.2f} minutes.")
                logging.info(f"Slept for {random_sleep_time / 60:.2f} minutes.")

if __name__ == "__main__":
    # main()
    try:
        scrape()
    except httpx.ConnectError | httpx.ProxyError as e1:
        logging.error(e1)
        scrape()
    except Exception as e:
        logging.critical(e)
        raise e