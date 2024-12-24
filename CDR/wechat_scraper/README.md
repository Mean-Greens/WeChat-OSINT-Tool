# Set up Virtual Environment
## Windows
`pip install -r windows_requirements.txt`
## Linux
`pip install -r linux_requirements.txt`

# Set up proxy list
Running `proxy_list.py` will scrape open source proxy sites and gather a list of proxies in `./proxies_list.txt`. Alternatively you can add your own proxy list to `./proxies_list.txt`, with one proxy per line.

# Scrape with the spider
## Command line output
`scrapy crawl <spider name>`
## File output
`scrapy crawl <spider_name> -O <file_name>` (`-O` is used to overwrite the output file, `-o` is used to append to the output file)

example

`scrapy crawl wechat -O output.json`

# References
Source code for scrapy ([scrapy github](https://github.com/scrapy/scrapy/tree/master))

Source code for scrapy proxies ([scrapy-rotating-proxies github](https://github.com/TeamHG-Memex/scrapy-rotating-proxies))

Scrapy tutorial for beginners ([scrapy tutorial](https://www.youtube.com/watch?v=s4jtkzHhLzY&t=738s))

Proxies tutorial for scrapy ([scrapy proxy setup](https://www.youtube.com/watch?v=rAPS9yybGSs&list=PLBs3kUf0HmnD6-Hn41yQUJJ1_hHVrxxik&index=2))