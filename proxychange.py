import aiohttp
import asyncio
import random
import subprocess
import sys

async def download_proxies(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.text()
    except aiohttp.ClientError as e:
        print(f"Failed to download proxies from {url}: {e}")
        return ''

def update_proxychains_conf(proxies):
    conf_file = "/etc/proxychains.conf"
    with open(conf_file, 'r') as file:
        conf_content = file.read()

    proxy_types = ['http', 'socks4', 'socks5']

    for proxy_type in proxy_types:
        conf_content = '\n'.join(line for line in conf_content.split('\n') if not line.strip().startswith((f'{proxy_type}\t')))
        if proxies[proxy_type]:
            random.shuffle(proxies[proxy_type])
            for proxy in proxies[proxy_type]:
                ip, port = proxy.split(':')
                conf_content += f"\n{proxy_type}\t{ip}\t{port}"

    with open(conf_file, 'w') as file:
        file.write(conf_content)

def run_proxychains_command(command):
    proxychains_command = f"proxychains {command}"
    try:
        subprocess.run(proxychains_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running proxychains: {e}")
        sys.exit(1)

async def main():
    if len(sys.argv) < 2:
        print("Usage: python script_name.py 'your_command_here'")
        sys.exit(1)

    proxy_urls = {
        'http': "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all",
        'socks4': "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all",
        'socks5': "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all"
    }

    proxies = {}
    for proxy_type, url in proxy_urls.items():
        proxies[proxy_type] = (await download_proxies(url)).strip().split('\n')

    update_proxychains_conf(proxies)

    command_to_run = " ".join(sys.argv[1:])
    await run_proxychains_command(command_to_run)

if __name__ == "__main__":
    asyncio.run(main())
