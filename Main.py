import requests
import time
import ctypes
import threading
from colorama import Fore, Style, init

init()

view = 0
view_lock = threading.Lock()
proxies_lock = threading.Lock()
proxies_list = []
stop_event = threading.Event()

def fetch_proxies_from_url():
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

def update_console_title():
    try:
        with proxies_lock:
            title = f"Tips booster | Total Views: {view}"
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    except Exception:
        print(f"{Fore.RED}Failed to update console title.{Style.RESET_ALL}")

def send_request(proxy, url):
    global view
    while not stop_event.is_set():
        try:
            response = requests.get(
                url,
                proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
            )
            if response.status_code == 200:
                with view_lock:
                    view += 1
                update_console_title()
                print(f"{Fore.CYAN}Using proxy {proxy} | Status code {response.status_code} | Total views: {view}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Proxy {proxy} | status code {response.status_code}{Style.RESET_ALL}")
        except requests.exceptions.RequestException:
            print(f"{Fore.RED}Proxy {proxy} failed{Style.RESET_ALL}")
            with proxies_lock:
                if proxy in proxies_list:
                    proxies_list.remove(proxy)
            break

def start_threads(url):
    threads = []
    while not stop_event.is_set():
        with proxies_lock:
            if not proxies_list or stop_event.is_set():
                break
            proxy = proxies_list.pop(0)
        thread = threading.Thread(target=send_request, args=(proxy, url))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    view_counter_url = "" # your view counter url

    try:
        fetch_proxies_from_url()
        update_console_title()
        print(f"{Fore.GREEN}Starting {len(proxies_list)} threads.{Style.RESET_ALL}")
        start_threads(view_counter_url)
    except Exception:
        print(f"{Fore.RED}An unexpected error occurred.{Style.RESET_ALL}")