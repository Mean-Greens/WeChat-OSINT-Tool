import scrapy


class SogouSpider(scrapy.Spider):
    name = 'wechat'
    start_urls = ['https://weixin.sogou.com/weixin?ie=utf8&s_from=input&_sug_=n&_sug_type_=&type=2&query=%E9%A6%99%E8%95%89%E5%B8%83%E4%B8%81&w=01019900&sut=801&sst0=1734984381153&lkt=1%2C1734984381042%2C1734984381042']

    def parse(self, response):
        for article in response.css('ul.news-list').css('li'):
            url = article.css('div.txt-box').css('h3').css('a::attr(href)').get()

            yield {
                # For each field we store the html of the element to then parse later for the text
                'title': article.css('div.txt-box').css('h3').get(),
                'description': article.css('div.txt-box').css('p.txt-info').get(),
                'author': article.css('div.txt-box').css('div.s-p').css('span.all-time-y2').get(),
                'date': article.css('div.txt-box').css('div.s-p').css('span.s2').css('script::text').get(), # This is not html, but rather Javascript for the date and time of the article
                'url': url,
                'website': None
            }
        
        next_page = response.css('[id="sogou_next"]::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)