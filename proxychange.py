#!/usr/bin/env python3
import requests
from seleniumwire import webdriver
import threading
import random
import time

PROXY_URL = "https://proxylist.farhanaulianda.tech"
PROXY_TEST_URL = "https://www.example.com"
MAX_REQUESTS_PER_PROXY = 5
PROXY_TIMEOUT = 10

active_proxy = None
proxy_pool = []
terminate_testing = False
lock = threading.Lock()

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
        driver = webdriver.Firefox(
            seleniumwire_options={
                'proxy': {
                    'http': f'http://{proxy_ip}:{proxy_port}',
                    'https': f'https://{proxy_ip}:{proxy_port}',
                    'no_proxy': 'localhost,127.0.0.1'
                }
            },
            options=test_options
        )
        driver.get(PROXY_TEST_URL)
        print(f"Proxy {proxy_ip}:{proxy_port} is active.")
        # Additional checks like anonymity level validation and response time measurement can be added here.
        return driver
    except Exception as e:
        print(f"Proxy {proxy_ip}:{proxy_port} is inactive: {e}")
        return None

def test_proxy_thread(proxy):
    global active_proxy, terminate_testing
    proxy_ip = proxy['ip']
    proxy_port = proxy['port']
    driver = test_proxy(proxy_ip, proxy_port)
    if driver:
        with lock:
            active_proxy = driver
            proxy_pool.remove(proxy)

def proxy_rotation():
    global active_proxy, terminate_testing
    while True:
        time.sleep(30)
        with lock:
            if not terminate_testing and active_proxy:
                new_proxy = random.choice(proxy_pool)
                if new_proxy:
                    active_proxy.proxy = {
                        'http': f'http://{new_proxy["ip"]}:{new_proxy["port"]}',
                        'https': f'https://{new_proxy["ip"]}:{new_proxy["port"]}',
                        'no_proxy': 'localhost,127.0.0.1'
                    }
                    print(f"Switched to proxy {new_proxy['ip']}:{new_proxy['port']}")
                    
                    # Test if the new proxy is active
                    try:
                        active_proxy.get(PROXY_TEST_URL)
                        print(f"Proxy {new_proxy['ip']}:{new_proxy['port']} is active.")
                    except Exception as e:
                        print(f"Proxy {new_proxy['ip']}:{new_proxy['port']} is inactive: {e}")

def main():
    proxies = fetch_proxies_from_url(PROXY_URL)
    if not proxies:
        print("Failed to fetch proxies from the URL. Exiting...")
        return
    proxy_pool.extend(proxies)
    proxy_pool.append(None)
    rotation_thread = threading.Thread(target=proxy_rotation)
    rotation_thread.daemon = True
    rotation_thread.start()
    current_proxy_index = 0
    while not active_proxy and current_proxy_index < len(proxy_pool):
        proxy = proxy_pool[current_proxy_index]
        proxy_thread = threading.Thread(target=test_proxy_thread, args=(proxy,))
        proxy_thread.start()
        proxy_thread.join()
        current_proxy_index += 1
        with lock:
            if terminate_testing:
                break
    # Wait for all threads to finish
    main_thread = threading.current_thread()
    for thread in threading.enumerate():
        if thread is not main_thread:
            thread.join()

if __name__ == "__main__":
    main()

# Close the active driver after testing is done
if active_proxy:
    active_proxy.quit()
