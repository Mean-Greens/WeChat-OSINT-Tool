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
from get_vector_db import get_vector_db
from query import query
import hashlib

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
            'Cookie': 'SNUID=FE286BE87D7A5626C3AA75CD7DD2BBEF; SUID=1274BB807452A20B0000000067351D3C; SUID=183E28957CA5A20B000000006750B0DA; cuid=AAEUxdBJUAAAAAuipseedwEAvgU=; SUV=1733341404042076; ABTEST=0|1736522904|v1; ariaDefaultTheme=undefined',
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
        return result
    return wrapper

def timeConvert(unix_timestamp): 
    # Convert the Unix timestamp to a datetime object 
    dt = datetime.datetime.fromtimestamp(int(unix_timestamp)) 
    # Format the datetime object as a string 
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def get_html(url):
    with httpx.Client() as client:
        
        response = client.get(url, headers=HEADERS)

        if response.status_code != 200:
            print(f"Non-200 response: {url} - Status Code: {response.status_code}")
        
        return BeautifulSoup(response.text, 'html.parser')
    
def get_wechat_link(url):
    with httpx.Client() as client:
        
        response = client.get(url, headers=HEADERS)
        if response.status_code == 302:
            print(response.headers) 
            print("You have been blocked")
            exit()
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
            return None
        
def read_website(url):
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
        
        response = client.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            body = soup.body
            body_text = body.get_text(strip=True)
            normalized_text = unicodedata.normalize("NFKD", body_text)
            normalized_text = ' '.join(normalized_text.split())
            return normalized_text
        else:
            print(response.status_code)
            print("Failed to retrieve the website")
            return None
   
def sogou_searcher(query):

    documents = []
    print(query)
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
        website = read_website(link)
        if website == None:
            continue
        web_hash = hashlib.sha256(website.encode('utf-8')).hexdigest()
        metadata: Dict[str, Union[str, None]] = {
            "source": link,
            "title": title,
            "description": description,
            "author": author,
            "date": date,
            "hash": web_hash
        }
        doc = Document(page_content=website, metadata=metadata)
        
        documents.append(doc)

    return documents

def store_websites(documents:list):
    # store each document in a vector embedding database
    db = get_vector_db()

    for doc in documents:
        
        if document_exists_by_hash(db, doc.metadata.get("hash")):
            print("Document already exists")
        else:
            print("Adding document to DB")
            db.add_documents([doc])

    #db.add_documents(documents)
    #db.persist()

def document_exists_by_hash(vectorstore, hash_value):
    results = vectorstore.similarity_search_with_score(
        query="",
        k=1,
        filter={"hash": hash_value}
    )
    return bool(results)
    

@timer
def main():
    documents = sogou_searcher('香蕉布丁')
    store_websites(documents)

    # question = QUESTION
    # results = query(SEARCH_TERM)

    # print(results)

if __name__ == "__main__":
    main()