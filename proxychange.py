#!/usr/bin/env python3
import requests
from seleniumwire import webdriver

def fetch_proxies_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch proxies from URL: {e}")
        return []

def test_proxy(proxy_ip, proxy_port):
    try:
        test_options = webdriver.FirefoxOptions()
        test_options.add_argument(f'--proxy-server={proxy_ip}:{proxy_port}')

        test_driver = webdriver.Firefox(
            seleniumwire_options={'proxy': {
                'http': f'http://{proxy_ip}:{proxy_port}',
                'https': f'https://{proxy_ip}:{proxy_port}',
                'no_proxy': 'localhost,127.0.0.1'
            }},
            options=test_options
        )

        test_driver.get('https://www.google.com')
        print(f"Proxy {proxy_ip}:{proxy_port} is active.")
        return test_driver
    except:
        print(f"Proxy {proxy_ip}:{proxy_port} is inactive.")
        return None

if __name__ == "__main__":
    proxy_url = "https://proxy.farhanaulianda.tech"
    proxies = fetch_proxies_from_url(proxy_url)

    if not proxies:
        print("Failed to fetch proxies from the URL. Exiting...")
    else:
        for proxy in proxies:
            proxy_ip = proxy['ip']
            proxy_port = proxy['port']
            active_driver = test_proxy(proxy_ip, proxy_port)
            if active_driver:
                active_driver.get('https://www.google.com')
                input("Press Enter to close Firefox...")
                active_driver.quit()
                break  
