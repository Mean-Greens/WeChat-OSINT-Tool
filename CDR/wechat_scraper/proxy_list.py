import concurrent
import time
import httpx
import re
from bs4 import BeautifulSoup

def gather_proxy_list():
    regex = r"[0-9]+(?:\.[0-9]+){3}:[0-9]+"
    c = httpx.get("https://spys.me/proxy.txt")
    test_str = c.text
    a = re.finditer(regex, test_str, re.MULTILINE)
    with open("proxies_list.txt", 'w') as file:
        for i in a:
            print(i.group(),file=file)
            
    d = httpx.get("https://free-proxy-list.net/")
    soup = BeautifulSoup(d.content, 'html.parser')
    td_elements = soup.select('.fpl-list .table tbody tr td')
    ips = []
    ports = []
    for j in range(0, len(td_elements), 8):
        ips.append(td_elements[j].text.strip())
        ports.append(td_elements[j + 1].text.strip())
    with open("proxies_list.txt", "a") as myfile:
        for ip, port in zip(ips, ports):
            proxy = f"{ip}:{port}"
            print(proxy, file=myfile)

def check_proxy(proxy, file):

    proxy_url = f"http://{proxy}"

    # set up proxy mounts
    proxy_mounts = {
        "http://": httpx.HTTPTransport(proxy=proxy_url),
        "https://": httpx.HTTPTransport(proxy=proxy_url),
    }

    # Try a request with the proxy
    try:
        with httpx.Client(mounts=proxy_mounts) as client:
            response = client.get("https://httpbin.org/ip")
            print(proxy, file=file)
    except Exception as e:
        return

def main():
    gather_proxy_list()

    # time.sleep(1)

    # proxies = open('proxies_list.txt').read().splitlines()

    # with open("working_proxies_list.txt", 'w') as file:
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    #         futures = [executor.submit(check_proxy, proxy, file) for proxy in proxies[:100]] 
    #         concurrent.futures.wait(futures)

if __name__ == "__main__":
    main()