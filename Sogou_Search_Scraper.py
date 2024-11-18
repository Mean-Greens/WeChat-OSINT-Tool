# This file contains a hardcoded cookies which are required to bypass Sogou bot detection.
# We will attempt automatic creation/retrieval of this cookie later.
#
import httpx
import re
import time
from bs4 import BeautifulSoup

'''
pip install httpx beautifulsoup4
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

def get_html(url):
    with httpx.Client() as client:
        
        response = client.get(url, headers=HEADERS)

        if response.status_code != 200:
            print(f"Non-200 response: {url} - Status Code: {response.status_code}")
        
        return BeautifulSoup(response.text, 'html.parser')
    
def get_wechat_link(url):
    with httpx.Client() as client:
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0'
        #            }
        
        response = client.get(url, headers=HEADERS)
        if response.status_code == 302:
            print(response.headers) 
            print("You have been blocked")
            exit()
        elif response.status_code == 200:
            # print(response.headers)
            # print(response.text)
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
            return body_text        
        else:
            print(response.status_code)
            print("Failed to retrieve the website")
            return None

    
def sogou_searcher(query):

    links = []
    print(query)
    html = get_html(f'{BASE_URL_1}{query}{BASE_URL_2}')

    try:
        body = html.find('body')
        links_wrapper = body.find(id='wrapper')
        links_main = links_wrapper.find(id='main')
        news_box = links_main.find('div', class_='news-box')
        news_list = news_box.find('ul')
        news_sites = news_list.find_all('li')
        #print(news_sites)
    except:
        print("No search results were returned")
        return links
    
    for site in news_sites:
        link_box = site.find(class_='txt-box')
        link_tag = link_box.find('a', href=True)
        link = "https://weixin.sogou.com" + link_tag.get('href')
        links.append(get_wechat_link(link))
        link = ''

    return links
        
    #print(read_website(get_wechat_link(links[0])))

def main():

    query = '神隐特警队+漫画+或+电视剧'

    html = get_html(f'{BASE_URL_1}{query}{BASE_URL_2}')

    body = html.find('body')
    links_wrapper = body.find(id='wrapper')
    links_main = links_wrapper.find(id='main')
    news_box = links_main.find('div', class_='news-box')
    news_list = news_box.find('ul')
    news_sites = news_list.find_all('li')
    #print(news_sites)

    links = []

    for site in news_sites:
        link_box = site.find(class_='txt-box')
        link_tag = link_box.find('a', href=True)
        link = "https://weixin.sogou.com" + link_tag.get('href')
        links.append(get_wechat_link(link))
        link = ''

    for link in links:
        print(link)
        
    #print(read_website(get_wechat_link(links[0])))


if __name__ == "__main__":
    main()