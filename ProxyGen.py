import time
import requests
import os
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import socks
import socket

MAX_LATENCY = 150  # Maximum acceptable latency in milliseconds

if os.name == "nt":
    os.system("title SOCKS5 Proxy Gen")


def main():
    global MAX_WORKERS

    while True:
        print("""
        1 - Check socks5 proxies listed sites
        2 - Check socks5 proxies url list
        3 - Check latency of SOCKS5 proxies
        """)

        choice = int(input("Choice: "))  # Convert input to integer
        if choice == 1:
            MAX_WORKERS = int(input("Workers (5-15): "))
            file = input("File: ")
            print("")
            check_sites_list(file)
            break
        elif choice == 2:
            MAX_WORKERS = int(input("Workers (5-15): "))
            file = input("File: ")
            print("")
            check_proxy_list(file)
            break
        elif choice == 3:
            MAX_WORKERS = int(input("Workers (5-15): "))
            file = input("File: ")
            print("")
            check_latency(file)
            break
        else:
            print("Invalid choice")
            time.sleep(1)
            clear_console()


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def check_sites_list(file):
    with open(file, "r") as f:
        site_urls = f.readlines()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for site_url in site_urls:
            site_url = site_url.strip()
            proxy_list = get_proxy_list(site_url)
            if proxy_list:
                for proxy in proxy_list:
                    executor.submit(check_proxy, proxy)


def check_proxy_list(file):
    with open(file, "r") as f:
        proxy_urls = f.readlines()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for proxy_url in proxy_urls:
            proxy_url = proxy_url.strip()
            executor.submit(check_proxy, proxy_url)


def get_proxy_list(site_url):
    try:
        response = requests.get(site_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            proxy_list = [line.strip() for line in soup.get_text().split("\n") if line.strip()]
            return proxy_list
        else:
            print(f"\033[93m[?]\033[0m {site_url}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"\033[93m[?]\033[0m {site_url}")
        return []


def check_proxy(proxy_url):
    try:
        socks.set_default_proxy(socks.SOCKS5, proxy_url.split(':')[0], int(proxy_url.split(':')[1]))
        socket.socket = socks.socksocket
        response = requests.get("https://httpbin.org/ip", timeout=10)
        if response.status_code == 200:
            print(f"\033[32m[+]\033[0m {proxy_url}")
            with open("valid_socks5.txt", "a") as valid_file:
                valid_file.write(proxy_url + "\n")
        else:
            print(f"\033[31m[-]\033[0m {proxy_url}")
    except requests.exceptions.RequestException:
        print(f"\033[31m[-]\033[0m {proxy_url}")


def check_latency(file):
    with open(file, "r") as f:
        proxy_urls = f.readlines()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for proxy_url in proxy_urls:
            proxy_url = proxy_url.strip()
            executor.submit(check_latency_proxy, proxy_url)


def check_latency_proxy(proxy_url):
    try:
        ip = proxy_url.split(':')[0]
        output = os.popen(f'ping -n 4 {ip}').read()  # Ping the IP address 4 times
        latency_line = [line for line in output.split('\n') if 'Minimum' in line]
        if latency_line:
            latency = int(latency_line[0].split('=')[1].split('ms')[0])
            if latency < MAX_LATENCY:
                print(f"\033[32m[+]\033[0m {proxy_url} {latency}ms")
                with open("working_socks5.txt", "a") as valid_file:
                    valid_file.write(proxy_url + "\n")
            else:
                print(f"\033[33m[-]\033[0m {proxy_url} {latency}ms")
        else:
            print(f"\033[31m[-]\033[0m {proxy_url}")
    except Exception as ex:
        print(f"\033[93m[?]\033[0m {proxy_url}")


if __name__ == '__main__':
    main()
    input("\nPress any key to continue . . .")
