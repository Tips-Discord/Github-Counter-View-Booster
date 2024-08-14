import requests
import time
import ctypes
import threading
from colorama import Fore, Style, init; init()
import re

view = 0
view_lock = threading.Lock()
proxies_lock = threading.Lock()
proxies_list = []
stop_event = threading.Event()

def fetch_proxies():
    global proxies_list
    try:
        response = requests.get("https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format=ipport&format=text&timeout=5000", timeout=10)
        response.raise_for_status()
        new_proxies = [line.strip() for line in response.text.splitlines() if line.strip()]
        with proxies_lock:
            proxies_list.extend(new_proxies)
        print(f"{Fore.GREEN}Successfully loaded {len(new_proxies)} proxies.{Style.RESET_ALL}")
        time.sleep(2)
    except requests.exceptions.RequestException:
        print(f"{Fore.RED}Failed to fetch proxies.{Style.RESET_ALL}")

def update_title():
    try:
        with proxies_lock:
            title = f"Tips booster | Total Views: {view}"
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    except Exception:
        print(f"{Fore.RED}Failed to update console title.{Style.RESET_ALL}")

def send(proxy, url):
    global view
    while not stop_event.is_set():
        try:
            start = time.time()
            response = requests.get(
                url,
                proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
            )
            end = time.time()
            if response.status_code == 200:
                with view_lock:
                    view += 1
                update_title()
                print(f"{Fore.CYAN}Using proxy {proxy} | Status code {response.status_code} | Total views: {view} | Time: {end - start:.2f} seconds{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Proxy {proxy} | status code {response.status_code}{Style.RESET_ALL}")
        except requests.exceptions.RequestException:
            print(f"{Fore.RED}Proxy {proxy} failed{Style.RESET_ALL}")
            with proxies_lock:
                if proxy in proxies_list:
                    proxies_list.remove(proxy)
            break

def get_views(url):
    response = requests.get(url)
    if response.status_code == 200:
        start_views = re.search(r'<text x="102.5" y="14">([\d,]+)</text>', response.text).group(1)
        print(f"{Fore.GREEN}Starting views: {start_views}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Failed to get views: {response.status_code}{Style.RESET_ALL}")

def start_threads(url):
    threads = []
    while not stop_event.is_set():
        with proxies_lock:
            if not proxies_list or stop_event.is_set():
                break
            proxy = proxies_list.pop(0)

        thread = threading.Thread(target=send, args=(proxy, url))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    view_counter_url = input("Enter view counter url: ")

    try:
        get_views(view_counter_url)
        time.sleep(3)
        fetch_proxies()
        update_title()
        print(f"{Fore.GREEN}Starting {len(proxies_list)} threads.{Style.RESET_ALL}")
        start_threads(view_counter_url)
    except Exception:
        print(f"{Fore.RED}An unexpected error occurred.{Style.RESET_ALL}")
