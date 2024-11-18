'''
To avoid getting blocked save the cookies:

# Save storage state into the file.
storage = context.storage_state(path="state.json")

Then create a new context in playwright with those cookies:

# Create a new context with the saved storage state.
context = browser.new_context(storage_state="state.json")
'''

# This file contains a hardcoded cookie called SNUID and SUV which is required to bypass Sogou bot detection.
# We will attempt automatic creation/retrieval of this cookie later.
#
import json
import os
import re
import time
from bs4 import BeautifulSoup
import httpx
from playwright.sync_api import sync_playwright, expect

'''
pip install playwright httpx beautifulsoup4
python -m playwright install
'''

HEADERS =  {
            'Host': 'weixin.sogou.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'DNT': '1',
            'Sec-GPC': '1',
            'Connection': 'keep-alive',
            'Cookie': 'ABTEST=0|1731083541|v1; SNUID=F49F576CEBEDCD85A76017EBECE1B107; SUID=1874BB801953A20B00000000672E3D15; IPLOC=US; SUID=1874BB8026A6A20B00000000672E3D16',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Priority': 'u=0, i'
            }

BASE_URL_1 = 'https://weixin.sogou.com/weixin?type=2&s_from=input&query=' # query in chinese
QUERY = '神隱特偵組'

def print_request_headers(request):
    for header, value in request.headers.items():
        print(f"{header}: {value}")

def get_html(url):
    with httpx.Client() as client:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0',
            'Cookie': 'IPLOC=US; SNUID=E9854971F1F7D7AAA7CC2158F25F211E; cuid=AAF8FCm+TwAAAAuipm0bXgEAvgU=; SUV=1730998380594875'
                   }
        response = client.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Non-200 response: {url} - Status Code: {response.status_code}")
        
        return BeautifulSoup(response.text, 'html.parser')
    
def get_wechat_link(link_tag):
    global HEADERS

    url = "https://weixin.sogou.com" + link_tag.evaluate("element => element.getAttribute('href')")

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

    with sync_playwright() as pw:
        browser = pw.firefox.launch(headless = False)
        context = browser.new_context()
        page = context.new_page()
        title = ''
        medadata_information = ''
        main_article = ''

        # If the list scraper breaks, the try catch block will restart it
        try:
            page.goto(url)

            # Wait for the page to load completely
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            read_more_tag = page.locator('#js_share_source')
            if read_more_tag.count() > 0:
                read_more_tag.click()

                # Wait for the page to load completely
                page.wait_for_load_state('networkidle')
                time.sleep(2)

            title = page.locator('#activity-name').inner_text()
            medadata_information = page.locator('#meta_content').inner_text()
            main_article = page.locator('#js_content').inner_text()

        except:
            print("Something went wrong, exiting program.")
            raise Exception

        page.close()
        context.close()
        browser.close()
        return title, medadata_information, main_article

def sogou(page, query):
    global BASE_URL_1

    page.goto(f'{BASE_URL_1}{query}')

    # Wait for the page to load completely
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    body = page.locator('body')
    links_wrapper = body.locator('#wrapper')
    links_main = links_wrapper.locator('#main')
    news_box = links_main.locator('.news-box')
    news_list = news_box.locator('ul')
    news_sites = news_list.locator('li').all()

    links = []

    for site in news_sites:
        link_box = site.locator('.txt-box')
        link_tag = link_box.locator('a')
        links.append(get_wechat_link(link_tag))
        link = ''

    return links


def main(query):
    query_links = []

    # Create new playwright instance
    with sync_playwright() as pw:
        browser = pw.firefox.launch(headless = False)
        context = browser.new_context(storage_state=f"{os.path.dirname(os.path.abspath(__file__))}\\state.json")
        page = context.new_page()

        # If the list scraper breaks, the try catch block will restart it
        try:
            query_links.append(sogou(page, query))
        except:
            print("Something went wrong, exiting program.")
            raise Exception

        page.close()
        context.close()
        browser.close()

    title, medadata, article = read_website(query_links[0][2])

    print(title)
    print(medadata)
    print(article)


if __name__ == "__main__":    
    main(QUERY)
