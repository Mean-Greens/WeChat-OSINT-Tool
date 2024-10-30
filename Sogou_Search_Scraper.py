# This file contains a hardcoded cookie called SNUID which is required to bypass Sogou bot detection.
# We will attempt automatic creation/retrieval of this cookie later.
#
import httpx
import re
from bs4 import BeautifulSoup

'''
pip install httpx beautifulsoup4
'''

BASE_URL_1 = 'https://weixin.sogou.com/weixin?type=2&s_from=input&query=' # query in chinese
#BASE_URL_2 = '&ie=utf8&_sug_=y&_sug_type_=&w=01019900&sut=3025&sst0=1730299585404&lkt=0%2C0%2C0'

def get_html(url):
    with httpx.Client() as client:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
        response = client.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Non-200 response: {url} - Status Code: {response.status_code}")
        
        return BeautifulSoup(response.text, 'html.parser')
    
def get_wechat_link(url):
    with httpx.Client() as client:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0',
            'Cookie': 'IPLOC=CN; SNUID=F69A556EEEE8C85C5B9B054DEEAEFDD4'
                   }
        
        response = client.get(url, headers=headers)
        if response.status_code == 302:
            print(response.headers) 
        elif response.status_code == 200:
            # print(response.headers)
            # print(response.text)
            WCUrl = ""
            pattern = r"url \+= '(.*?)';"
            matches = re.findall(pattern, response.text)
            for match in matches:
                WCUrl += match

            print(WCUrl)
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

    
def main():

    query = '习近平'

    html = get_html(f'{BASE_URL_1}{query}')

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
        #print(link)
        links.append(link)
        link = ''
        
    print(read_website(get_wechat_link(links[0])))


if __name__ == "__main__":
    main()

