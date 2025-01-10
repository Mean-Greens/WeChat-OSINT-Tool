# This file contains a hardcoded cookies which are required to bypass Sogou bot detection.
# We will attempt automatic creation/retrieval of this cookie later.
#
import datetime
import uuid
import httpx
import re
import time
from bs4 import BeautifulSoup
import os
import ollama
import chromadb

'''
pip install httpx beautifulsoup4 ollama chromadb
'''
HEADERS = {
            'Host': 'weixin.sogou.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'DNT': '1',
            'Sec-GPC': '1',
            'Connection': 'keep-alive',
            'Cookie': 'ABTEST=0|1731534140|v1; SNUID=4B2DE1D95A5F7C8B6C389B795A602AC5; SUID=1274BB807452A20B0000000067351D3C; ariaDefaultTheme=undefined',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Priority': 'u=0, i'
                   }
BASE_URL_1 = 'https://weixin.sogou.com/weixin?type=2&s_from=input&query=' # query in chinese
BASE_URL_2 = '&ie=utf8'

QUESTION = '哪种香蕉布丁最好吃？' # Which banana pudding is best?
SEARCH_TERM_OLD = '香蕉布丁' # Banana pudding
SEARCH_TERM = '冰淇淋' # Ice cream

# Get the directory path of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the 'db' folder to the directory path
db_path = os.path.join(current_dir, 'db')

client = chromadb.PersistentClient(path=db_path)

collection = client.get_or_create_collection(name="demo")

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

def read_search_terms():
    with open('Wordlist.txt', 'r', encoding='utf-8') as f:
        search_terms = f.readlines()
        for i, term in enumerate(search_terms):
            search_terms[i] = term.strip()
        search_terms = list(set(list(filter(None, search_terms))))
    return search_terms

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
            print("Failed to retrieve the link")
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
            return body_text        
        else:
            print(response.status_code)
            print("Failed to retrieve the website")
            return None
   
def sogou_searcher(query):

    links = []
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
        return links
    
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
        links.append(get_wechat_link(link))
        link = ''

    for link in links:
        if link == None:
            continue
        website = read_website(link)
        if website == None:
            continue
        web_hash = hash(website)
        documents.append([link, website, title, description, author, date, web_hash])

    return documents

def store_websites(documents:list):
    # store each document in a vector embedding database
    for i, d in enumerate(documents):
        # Check the hash to see if it is already in the database
        hash_value = d[6]
        articles_by_hash = query_articles_by_hash(hash_value)
        
        if len(articles_by_hash['documents'][0]) != 0:
            continue

        response = ollama.embeddings(model="mxbai-embed-large", prompt=d[1])
        embedding = response["embedding"]
        collection.add(
            ids=[f'{uuid.uuid5(uuid.NAMESPACE_URL, d[0])}'],
            embeddings=[embedding],
            metadatas=[{"url": f'{d[0]}',
                        "title": f'{d[2]}',
                        "description": f'{d[3]}',
                        "author": f'{d[4]}',
                        "date": f'{d[5]}',
                        "hash": f'{d[6]}'}],
            documents=[d[1]]
        )

def get_articles(question:str):
    # generate an embedding for the prompt and retrieve the most relevant doc
    response = ollama.embeddings(
    model="mxbai-embed-large",
    prompt=question
    )
    results = collection.query(
        query_embeddings=[response["embedding"]],
        n_results=3
    )
    return results['documents']

def query_articles_by_hash(hash_value):
    # generate an embedding for the prompt and retrieve the most relevant doc
    response = ollama.embeddings(
    model="mxbai-embed-large",
    prompt="This prompt does not matter"
    )

    # Define the filter 
    filter_by_hash = {"hash": hash_value} 
    
    # Query the collection, ensuring to include 'documents' and 'metadatas'
    results = collection.query(
        query_embeddings=[response["embedding"]],
        where=filter_by_hash,
        # include=['documents', 'metadatas'] # Specify which fields to include in the response
    )
    return results

@timer
def main(search_term):
    documents = sogou_searcher(search_term)
    store_websites(documents)
    
    # question = QUESTION
    # results = get_articles(question)

    # print(results)

if __name__ == "__main__":
    # main()
    queries = read_search_terms()
    for query in queries:
        main(query)
        time.sleep(300) # Sleep for 5 minutes to avoid being blocked