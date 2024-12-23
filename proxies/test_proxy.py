import httpx
from bs4 import BeautifulSoup

def get_html(url, proxy=None):
    proxies = {
        "http://": f"http://{proxy}" if proxy else None,
        "https://": f"http://{proxy}" if proxy else None,
    }
    
    try:
        # Use a list of reliable proxies if one fails
        proxy_list = [
            '103.234.35.142:8090',
            '51.91.109.83:80',
            '190.97.252.18:999',
            '38.194.236.168:3128',
            '54.36.229.122:8080',
            '175.158.57.136:7788',
            '222.127.51.132:8082',
            '121.136.189.231:60001',
            '27.131.250.252:8080',
            '38.156.15.160:999',
            '101.98.17.89:3128',
            '2.135.237.106:8080',
            '190.61.101.72:8080',
            '185.25.22.185:3128',
            '124.40.249.43:8080',
            '147.182.180.242:80',
            '90.156.194.71:8080',
            '103.149.118.51:8080',
            '77.242.177.57:3128',
            '185.126.5.72:8080',
            '200.41.170.212:11201',
            '37.232.13.2:8080',
            '14.241.237.219:8080',
            '103.164.229.138:8085',
            '45.179.71.76:667',
            '186.96.101.75:999',
            '188.209.244.24:8080',
            '101.108.7.72:8080',
            '176.9.239.181:80',
            '77.242.30.9:8088',
            '125.26.225.196:8080',
            '103.76.108.96:8080',
            '95.164.16.142:3128',
            '113.203.238.82:8080',
            '46.10.209.230:8080',
            '206.201.3.83:8095'
        ]
        
        for proxy_addr in proxy_list:
            try:
                with httpx.Client(
                    proxies=proxies, 
                    timeout=httpx.Timeout(30.0, connect=10.0)
                ) as client:
                    response = client.get(url)
                    
                    if response.status_code == 200:
                        return BeautifulSoup(response.text, 'html.parser')
                    
                    print(f"Non-200 response with proxy {proxy_addr}: Status Code: {response.status_code}")
            
            except (httpx.HTTPStatusError, httpx.RequestError, Exception) as e:
                print(f"Error with proxy {proxy_addr}: {e}")
        
        print("All proxy attempts failed.")
        return None

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def main():
    html = get_html('https://weixin.sogou.com/weixin?p=01030402&query=%E7%8C%AB&type=2&ie=utf8')

    if html is not None:
        print(html.prettify())
    else:
        print("Failed to retrieve the HTML content.")

if __name__ == "__main__":
    main()