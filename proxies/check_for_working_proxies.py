import asyncio
import httpx

proxies = open('proxy_list.txt').read().splitlines()

async def check_proxy(proxy):

    proxies_1 = {
        "http://": f"http://{proxy}",
        "https://": f"http://{proxy}",
    }

    # make a request using the selected proxy
    try:
        async with httpx.AsyncClient(proxies=proxies_1, timeout=5.0, verify=False) as client:
            response = await client.get("https://httpbin.org/ip")
            response.raise_for_status()
            print(f"Proxy {proxy} is working.")
    except (httpx.RequestError, httpx.HTTPStatusError) as exc:
        return
        print(f"Proxy {proxy} failed: {exc}")

async def main():
    tasks = [check_proxy(proxy) for proxy in proxies] 
    await asyncio.gather(*tasks)

asyncio.run(main())