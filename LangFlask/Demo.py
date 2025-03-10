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
# from MGHTMLLoader import MGHTMLLoader
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

# From rich.traceback this shows errors in a cleaner more readable way
install(show_locals=False)

# Creates a log file for the Wechat web scraper
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
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Referer': 'https://www.sogou.com/',
            'Connection': 'keep-alive',
            'Cookie': 'IPLOC=NL; SUID=8CFD08D41AA7A20B000000006781FE67; cuid=AAHKs2cKUQAAAAuipsd9DwIA4wQ=; SUV=1736572520882172; ABTEST=0|1736572526|v1; SNUID=6FC3B7B802072DC4CDB80D110208C9E5; ariaDefaultTheme=undefined',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-site',
            'Priority': 'u=0, i'
        }


BASE_URL_1 = 'https://weixin.sogou.com/weixin?type=2&s_from=input&query=' # query in chinese
BASE_URL_2 = '&ie=utf8'

# QUESTION = '哪种香蕉布丁最好吃？' # Which banana pudding is best?
# SEARCH_TERM = '香蕉布丁' # Banana pudding

from constants import FORCE_WORDLIST_RESTART

# Get the directory path of the current file
#current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the 'db' folder to the directory path
#db_path = os.path.join(current_dir, 'db')

#client = chromadb.PersistentClient(path=db_path)

#collection = client.get_or_create_collection(name="demo")

def timer(func):
    """
    A decorator that measures and logs the execution time of a function.

    The decorator calculates the time taken for a wrapped function to execute and
    formats the duration into hours, minutes, and seconds. It prints the elapsed time
    to the console and logs it using the logging module.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The wrapped function with execution time measurement functionality.

    Example:
        @timer
        def my_function():
            # Function code here...

        my_function()
        # Output: --- 0 hours, 0 minutes, 0.05 seconds ---
    """
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

def force_wordlist():
    global FORCE_WORDLIST_RESTART
    FORCE_WORDLIST_RESTART = True
    return

def read_search_terms():
    """
    Reads a list of search terms from 'Wordlist.txt' and filters them to include every 
    other term starting with the second one, focusing on Chinese terms.

    The function removes any blank lines from the file, strips whitespace from each term,
    selects every second term starting with the second one, and eliminates duplicates 
    while preserving the order.

    Returns:
        list: A list of unique Chinese search terms extracted from 'Wordlist.txt'.

    Example:
        # Assuming 'Wordlist.txt' contains:
        # apple
        # 苹果
        # banana
        # 香蕉
        # orange
        # 橙子

        result = read_search_terms()
        # Output: ['苹果', '香蕉', '橙子']
    """
    with open('Wordlist.txt', 'r', encoding='utf-8') as f:
        search_terms = f.readlines()
        for i, term in enumerate(search_terms):
            search_terms[i] = term.strip()
        search_terms = list(filter(None, search_terms))
        chinese_search_terms = search_terms[1::2]
        unique_search_terms = list(OrderedDict.fromkeys(chinese_search_terms))
    return unique_search_terms

def timeConvert(unix_timestamp): 
    # Convert the Unix timestamp to a datetime object 
    dt = datetime.datetime.fromtimestamp(int(unix_timestamp)) 
    # Format the datetime object as a string 
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def get_html(url, retries=5, wait_time=120):
    """
    Fetches the HTML content of the specified URL with retry logic for handling timeouts.

    The function attempts to retrieve the HTML content of the given URL up to a specified 
    number of retries. If a timeout occurs, it waits for a specified duration before retrying. 
    Logs are generated for timeout occurrences, non-200 HTTP responses, and critical failures 
    if the maximum number of retries is exceeded. The HTML content and a parsed BeautifulSoup 
    object are returned.

    Args:
        url (str): The URL to fetch the HTML content from.
        retries (int, optional): The maximum number of retry attempts in case of a ReadTimeout. 
                                 Defaults to 5.
        wait_time (int, optional): The wait time in seconds between retry attempts. Defaults to 120.

    Returns:
        tuple: A tuple containing:
               - content (bytes): The raw HTML content of the response.
               - soup (BeautifulSoup): A BeautifulSoup object for parsing the HTML content.

    Raises:
        Exception: Raised if the function fails to fetch the URL after the maximum number of retries.

    Example:
        try:
            content, soup = get_html("https://example.com")
            print(soup.title.string)
        except Exception as e:
            print("Failed to fetch the URL:", e)
    """
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
        
        return response.content, BeautifulSoup(response.text, 'html.parser')

def get_wechat_link(url):
    """
    Retrieves the WeChat link from the specified URL.

    The function sends a GET request to the specified URL using the httpx library. It handles
    different HTTP response status codes:
    - If the status code is 302, it logs an error indicating that access has been blocked and
      returns None.
    - If the status code is 200, it searches for and reconstructs the WeChat link using a 
      regular expression pattern found in the HTML response.
    - If the response code is anything else, it logs an error and returns None.

    Args:
        url (str): The URL to fetch and parse for the WeChat link.

    Returns:
        str or None: The extracted WeChat link as a string if found, or None if the link cannot
        be retrieved.

    Example:
        wechat_link = get_wechat_link("https://example.com")
        if wechat_link:
            print("WeChat Link:", wechat_link)
        else:
            print("Failed to retrieve WeChat link.")
    """
    with httpx.Client(timeout=httpx.Timeout(60.0)) as client:
        
        response = client.get(url, headers=HEADERS)
        if response.status_code == 302:
            print(response.headers) 
            print("You have been blocked")
            logging.error(response.headers)
            logging.error("You have been blocked")
            return None
        elif response.status_code == 200:
            WCUrl = ""
            pattern = r"url \+= '(.*?)';" #Regular Expression to match the wechat link in the response
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
        

#Appears to pull the entire website, not just the HTML. I don't know if that's a hundred percent true though.
#We could probably combine this function with the Read_HTML function.
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
    """
    Performs a Sogou search using the provided query and retrieves the search results.

    The function sends a GET request to the Sogou search engine, extracts relevant information
    (e.g., title, description, author, date, and source link) from the search results, and
    processes the links to WeChat articles. The content and metadata for each retrieved article
    are packaged into documents for further use.

    Args:
        query (str): The search keyword or term to query on Sogou.

    Returns:
        list: A list of documents where each document consists of:
              - Document for the raw webpage content.
              - Document for the normalized text content, each with associated metadata.

    Metadata Keys:
        - source (str): The source URL of the WeChat article.
        - title (str): The title of the article.
        - description (str): A brief description of the article.
        - author (str): The author of the article.
        - date (str): The publication date of the article in timestamp format.
        - hash (str): A SHA-256 hash of the normalized content for deduplication.
        - keyword (str): The search keyword used for querying.

    Raises:
        None directly. Logs warnings or errors when no results are found or if an issue occurs
        during processing.

    Example:
        query = "example query"
        documents = sogou_searcher(query)
        if documents:
            print(f"Retrieved {len(documents)} documents.")
        else:
            print("No documents were retrieved.")
    """

    documents = []
    print(query)
    logging.info(query)
    content, html = get_html(f'{BASE_URL_1}{query}{BASE_URL_2}')

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

        #This part formats the found links from the scraped page to then get the WeChat link
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
            "hash": web_hash,
            "keyword": query
        }

    
        doc = [Document(page_content=website, metadata=metadata), Document(page_content=normalized_text, metadata=metadata)]
        
        documents.append(doc)

    return documents

def store_websites(documents:list):
    """
    Stores each document into a vector embedding database for further use and analysis.

    The function checks if a document already exists in the vector database by comparing its
    hash. If the document does not exist, it adds only its metadata to save storage space, 
    chunks the document for better compatibility with large language models (LLMs), and stores
    these chunks in a separate chunked collection. Additionally, the function saves the HTML
    content of each document as a file in an 'Articles' folder on the desktop.

    Args:
        documents (list): A list of documents where each document consists of:
            - doc[0]: An object containing metadata (e.g., hash and other information).
            - doc[1]: The content of the document to be chunked and stored.

    Returns:
        None

    Side Effects:
        - Logs messages to indicate the status of document storage.
        - Writes HTML content files to the 'Articles' folder on the desktop.
        - Updates vector embedding databases with document metadata and chunks.

    Example:
        documents = [
            (Document(page_content="<html>...</html>", metadata={"hash": "123abc"}), chunked_doc)
        ]
        store_websites(documents)
        # Adds metadata and chunks to the database, and saves the HTML file locally.
    """
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
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200) #Original 500, 100
            chunks = text_splitter.split_documents([chunk_doc])
            db_chunked.add_documents(chunks)

            # Save the HTML file to an Articles folder on the desktop
            Path(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), f'Articles/{doc[0].metadata.get("hash")}.html')).write_text(doc[0].page_content, encoding='utf-8')

# checks to see if a document is in the VectorDB already using the hash
def document_exists_by_hash(vectorstore, hash_value):
    results = vectorstore.get(where={"hash": hash_value})  # Direct metadata lookup
    return bool(results["documents"])  # Check if any documents exist

#Main function to make everything run
@timer
def main(search_term):
    documents = sogou_searcher(search_term)
    store_websites(documents)

def scrape():
    """
    Main function for scraping data from a wordlist.

    This function iterates over a list of search queries, obtained from `read_search_terms()`,
    and processes each query by calling the `main()` function. If the `FORCE_WORDLIST_RESTART` 
    global flag is set, the function resets the flag and refreshes the wordlist. In case of a 
    `httpx.ConnectError`, the error is logged, and the function continues with the next query. 
    After processing each query, the function waits for a random time between 15 and 20 minutes 
    before proceeding to the next one.

    Args:
        None

    Returns:
        None

    Side Effects:
        - Continuously runs in a loop until interrupted.
        - Reads and processes search queries from a wordlist.
        - Logs any connection errors or sleep intervals.
        - Waits for a random interval after each query.

    Example:
        # Call the scrape function to start processing queries:
        scrape()
    """
    global FORCE_WORDLIST_RESTART
    while True:
            # This refreshes the wordlist after all terms are scraped
            queries = read_search_terms()

            for query in reversed(queries):
                if FORCE_WORDLIST_RESTART:
                    FORCE_WORDLIST_RESTART = False
                    break
                
                try:
                    # Calls the main function which will call all the other functions needed to 
                    # complete scraping. 
                    main(query)
                except httpx.ConnectError as e:
                    print(f"ConnectError occurred: {e}")
                    logging.error(f"ConnectError occurred: {e}")
                    continue  # Retry the next query

                # Generate a random time between 15 and 20 minutes (in seconds)
                random_sleep_time = random.uniform(15 * 60, 20 * 60)
                
                # Sleep for the random time
                time.sleep(random_sleep_time)
                print(f"Slept for {random_sleep_time / 60:.2f} minutes.")
                logging.info(f"Slept for {random_sleep_time / 60:.2f} minutes.")

if __name__ == "__main__":
    try:
        scrape()
    except (httpx.RequestError, httpx.ConnectError, httpx.ProxyError, httpx.ReadTimeout, httpx.ConnectTimeout, httpx.HTTPStatusError) as e1:
        logging.error(e1)

        # Generate a random time between 15 and 20 minutes (in seconds)
        random_sleep_time = random.uniform(15 * 60, 20 * 60)
        
        # Sleep for the random time
        time.sleep(random_sleep_time)
        
        scrape()
    except Exception as e:
        logging.critical(e)
        raise e