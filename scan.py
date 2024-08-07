import requests
import threading
from termcolor import colored
import time
import re
import os

def clear():
    os.system("cls") if os.name == "nt" else os.system("clear")

clear()

class ProxyInfo:
    def __init__(self, proxy):
        self.proxy = proxy
        self.location = None
        self.type = None
        self.response_time = None
        self.country = None
        self.org = None

    def determine_location(self):
        try:
            response = requests.get('https://ipinfo.io/json', proxies={"http": self.proxy, "https": self.proxy}, timeout=15)
            data = response.json()
            self.location = data.get("city", "Unknown")
            self.country = data.get("country", "Unknown")
            self.org = data.get("org", "Unknown")
            return True
        except:
            self.location = "Unknown"
            self.country = "Unknown"
            self.org = "Unknown"
            return False

    def determine_type(self):
        types = ["http", "https"]
        for t in types:
            try:
                response = requests.get("https://ipinfo.io/json", proxies={t: self.proxy}, timeout=15)
                if response.status_code == 200:
                    self.type = t.upper()
                    return
            except:
                pass
        self.type = "Unknown"

    def measure_response_time(self):
        try:
            response = requests.get("https://ipinfo.io/json", proxies={"http": self.proxy, "https": self.proxy}, timeout=15)
            self.response_time = response.elapsed.total_seconds()
        except:
            self.response_time = float('inf')

    def get_info(self):
        is_live = self.determine_location()
        if is_live:
            self.determine_type()
            self.measure_response_time()
        return is_live

def fetch_proxies_from_links(file_with_links, output_file):
    proxy_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$')
    with open(file_with_links, 'r', encoding='ISO-8859-1') as file:
        links = file.readlines()
    
    all_proxies = set()
    for link in links:
        link = link.strip()
        try:
            response = requests.get(link)
            if response.status_code == 200:
                proxies = response.text.splitlines()
                for proxy in proxies:
                    proxy = proxy.strip()
                    if proxy_pattern.match(proxy):
                        all_proxies.add(proxy)
                # Lưu proxy vào tệp ngay sau khi lấy được
                with open(output_file, 'a') as file:
                    for proxy in all_proxies:
                        file.write(f"{proxy}\n")
                all_proxies.clear()
        except requests.RequestException:
            print(colored(f"Failed to fetch from {link}", "red"))

def check_live_proxies(filename, num_threads):
    proxy_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$')
    lock = threading.Lock()

    def check_proxy_thread(proxy):
        proxy_info = ProxyInfo(proxy)
        if proxy_info.get_info():
            if proxy_pattern.match(proxy):
                clear()
                print(f"""
\x1b[38;2;255;0;0mP\x1b[38;2;224;30;30mr\x1b[38;2;193;61;61mo\x1b[38;2;163;91;91mx\x1b[38;2;132;122;122my\x1b[38;2;102;153;153m:\x1b[38;2;71;183;183m \x1b[38;2;40;214;214m{proxy}\x1b[0m
\x1b[38;2;255;0;0mC\x1b[38;2;229;25;25mo\x1b[38;2;204;51;51mu\x1b[38;2;178;76;76mn\x1b[38;2;153;102;102mt\x1b[38;2;127;127;127mr\x1b[38;2;102;153;153my\x1b[38;2;76;178;178m:\x1b[38;2;51;204;204m \x1b[38;2;25;229;229m{proxy_info.country}\x1b[0m
\x1b[38;2;255;0;0mI\x1b[38;2;214;40;40mS\x1b[38;2;173;81;81mP\x1b[38;2;132;122;122m:\x1b[38;2;91;163;163m \x1b[38;2;51;204;204m{proxy_info.org}\x1b[0m
\x1b[38;2;255;0;0mL\x1b[38;2;232;22;22mo\x1b[38;2;209;45;45mc\x1b[38;2;186;68;68ma\x1b[38;2;163;91;91mt\x1b[38;2;140;114;114mi\x1b[38;2;117;137;137mo\x1b[38;2;94;160;160mn\x1b[38;2;71;183;183m:\x1b[38;2;48;206;206m \x1b[38;2;25;229;229m{proxy_info.location}\x1b[0m
\x1b[38;2;255;0;0mT\x1b[38;2;219;35;35my\x1b[38;2;183;71;71mp\x1b[38;2;147;107;107me\x1b[38;2;112;142;142m:\x1b[38;2;76;178;178m \x1b[38;2;40;214;214m{proxy_info.type}\x1b[0m""")
                with lock:
                    with open("live.txt", "a") as file:
                        file.write(proxy + "\n")
            else:
                print(colored(f" {proxy} - Định dạng không hợp lệ", "yellow"))
        else:
            clear()
            print(colored(f"IP: {proxy} Checked proxy not working", "red"))

    with open(filename, 'r', encoding='ISO-8859-1') as file:
        proxies = file.readlines()
        threads = []

        for proxy in proxies:
            proxy = proxy.strip()
            thread = threading.Thread(target=check_proxy_thread, args=(proxy,))
            thread.start()
            threads.append(thread)

            if len(threads) >= num_threads:
                for thread in threads:
                    thread.join()
                threads = []

        for thread in threads:
            thread.join()

    with open("live.txt", "r") as f:
        lines = f.read().splitlines()

    print("Total Proxy Live:", len(lines))
    print("Đã lưu vào file live.txt")

if __name__ == "__main__":
    try:
        clear()
        fetch_proxies_from_links("link.txt", "proxy.txt")
        print("Proxy list saved to proxy.txt.")
        time.sleep(1)
        num_threads = 1000
        check_live_proxies("proxy.txt", num_threads)
    except KeyboardInterrupt:
        print("Exiting... Please wait a moment...")
        time.sleep(1)
        exit()
