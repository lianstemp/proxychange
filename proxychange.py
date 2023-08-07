import requests
from seleniumwire import webdriver

def fetch_proxies_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        proxies = response.json()
        return proxies
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch proxies from URL: {e}")
        return []

def test_proxy(proxy_ip, proxy_port):
    try:
        # Mengatur proxy untuk pengujian
        test_options = webdriver.FirefoxOptions()
        test_options.add_argument(f'--proxy-server={proxy_ip}:{proxy_port}')

        # Menginisialisasi peramban Firefox untuk pengujian proxy
        test_driver = webdriver.Firefox(seleniumwire_options={'proxy': {
            'http': f'http://{proxy_ip}:{proxy_port}',
            'https': f'https://{proxy_ip}:{proxy_port}',
            'no_proxy': 'localhost,127.0.0.1'  # Bypass the proxy for local addresses
        }}, options=test_options)

        # Pengujian proxy dengan membuka Google
        test_driver.get('http://ipecho.net/plain')

        # Jika berhasil membuka Google, proxy aktif
        print(f"Proxy {proxy_ip}:{proxy_port} is active.")
        return test_driver
    except:
        # Jika terjadi error, proxy tidak aktif
        print(f"Proxy {proxy_ip}:{proxy_port} is inactive.")
        return None

if __name__ == "__main__":
    proxy_url = "https://proxy.farhanaulianda.tech"

    # Membaca daftar proxy dari URL
    proxies = fetch_proxies_from_url(proxy_url)

    if not proxies:
        print("Failed to fetch proxies from the URL. Exiting...")
    else:
        active_driver = None

        for proxy in proxies:
            proxy_ip = proxy['ip']
            proxy_port = proxy['port']

            if not active_driver:
                active_driver = test_proxy(proxy_ip, proxy_port)
                if active_driver:
                    break  # Berhenti mencari proxy yang aktif 

        if active_driver:
            # Buka url pengujian IP
            active_driver.get('http://ipecho.net/plain')

            # Biarkan jendela Firefox terbuka selama beberapa saat
            input("Tekan Enter untuk menutup Firefox...")
            active_driver.quit()
