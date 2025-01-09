import datetime
import re
import time
import httpx
from bs4 import BeautifulSoup
import scrapy

'''
pip install httpx beautifulsoup4 ollama chromadb scrapy scrapy-rotating-proxies
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

def get_wechat_link(url):
    with httpx.Client() as client:
        
        response = client.get(url, headers=HEADERS)
        if response.status_code == 302:
            print(response.headers)
            print(url)
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


class SogouSpider(scrapy.Spider):
    name = 'wechat'
    start_urls = ['https://weixin.sogou.com/weixin?ie=utf8&s_from=input&_sug_=n&_sug_type_=&type=2&query=%E9%A6%99%E8%95%89%E5%B8%83%E4%B8%81&w=01019900&sut=801&sst0=1734984381153&lkt=1%2C1734984381042%2C1734984381042']

    def parse(self, response):
        for article in response.css('ul.news-list').css('li'):
            link = article.css('div.txt-box').css('h3').css('a::attr(href)').get()
            url = get_wechat_link(f'https://weixin.sogou.com{link}')

            yield {
                # For each field we store the html of the element to then parse later for the text
                'title': article.css('div.txt-box').css('h3').get(),
                'description': article.css('div.txt-box').css('p.txt-info').get(),
                'author': article.css('div.txt-box').css('div.s-p').css('span.all-time-y2').get(),
                'date': article.css('div.txt-box').css('div.s-p').css('span.s2').css('script::text').get(), # This is not html, but rather Javascript for the date and time of the article
                'url': url,
                'website': read_website(url)
            }
        
        next_page = response.css('[id="sogou_next"]::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)