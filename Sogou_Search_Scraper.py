import httpx
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
        print(link)
        links.append(link)
        link = ''


    # get_page_data(links[0])

    # with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    #     futures = [executor.submit(process_region, f'https://onlinesys.necta.go.tz/results/2023/sfna/{link[1]}', link[0]) for link in region_links]
    #     # futures = [executor.submit(process_region, f'https://onlinesys.necta.go.tz/results/2023/sfna/{link[1]}', link[0]) for link in region_links[:2]] # For testing only, limiting the number of loops
    #     concurrent.futures.wait(futures)

    # print('Finished collecting data')

if __name__ == "__main__":
    main()




# &amp;type=2&amp;query=%E5%A5%A5%E8%BF%90%E4%BC%9A%E9%87%91%E7%89%8C&amp;token=A46451CE988A9C26B4B296076721FFE3B484EDA56722588B
# &type=2&query=%E5%A5%A5%E8%BF%90%E4%BC%9A%E9%87%91%E7%89%8C&token=A46451CE988A9C26B4B296076721FFE3B484EDA56722588B