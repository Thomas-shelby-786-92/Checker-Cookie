import os
import json
import requests
from http.cookies import SimpleCookie
from colorama import Fore, Style, init
from tqdm import tqdm

init(autoreset=True)

BASE_URLS = {
    "netflix": {"url": "https://www.netflix.com/browse", "domain": ".netflix.com"},
    "spotify": {"url": "https://open.spotify.com/", "domain": ".spotify.com"}
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br, zstd"
}

def display_menu():
    print(Style.BRIGHT + Fore.BLUE + "\n📁 Cookie Validator\n")
    print(Fore.BLUE + "1. Netflix")
    print(Fore.BLUE + "2. Spotify")
    print(Fore.BLUE + "3. Discord Link")
    print(Fore.BLUE + "4. Exit")
    print(Fore.CYAN + "\nChoose an option: ", end='')

def is_cookie_valid(service, cookie_dict):
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        session.cookies.update(cookie_dict)

        url = BASE_URLS[service]["url"]
        response = session.get(url, allow_redirects=True)

        if response.status_code != 200:
            return False

        content = response.text.lower()

        if service == "netflix":
            return "profile-gate" in content or "/signout" in content

        elif service == "spotify":
            return "your library" in content or "account overview" in content

        return False
    except Exception as e:
        print(Fore.RED + f"Error checking cookie: {e}")
        return False

def convert_json_to_dict(cookie_data):
    return {c["name"]: c["value"] for c in cookie_data if "name" in c and "value" in c}

def convert_header_string_to_dict(header_str):
    cookie = SimpleCookie()
    cookie.load(header_str)
    return {key: morsel.value for key, morsel in cookie.items()}

def convert_netscape_to_dict(lines):
    cookies = {}
    for line in lines:
        if line.strip().startswith("#") or not line.strip():
            continue
        parts = line.strip().split('\t')
        if len(parts) >= 7:
            name = parts[5]
            value = parts[6]
            cookies[name] = value
    return cookies

def detect_format(text):
    try:
        data = json.loads(text)
        if isinstance(data, list) and all("name" in c and "value" in c for c in data):
            return "json", data
    except:
        pass
    if "HostOnly" in text or text.count('\t') >= 6:
        return "netscape", text.strip().splitlines()
    if "=" in text and ";" in text:
        return "header", text
    return "unknown", None

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        display_menu()
        choice = input().strip()

        if choice == '4':
            print(Fore.MAGENTA + "👋 Exiting... Goodbye!")
            break
        elif choice == '3':
            print(Fore.CYAN + "\n🔗 Join our Discord: https://discord.gg/JjDgy47Pkp")
            input(Fore.YELLOW + "\nPress Enter to return to menu...")
            continue
        elif choice not in ['1', '2']:
            print(Fore.RED + "❌ Invalid option. Please try again.")
            input(Fore.YELLOW + "Press Enter to continue...")
            continue

        service = "netflix" if choice == '1' else "spotify"
        domain_required = BASE_URLS[service]['domain']

        # Get the folder where the script is running from
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Look for cookies folder inside the script directory
        cookies_folder = os.path.join(script_dir, "cookies")

        print(Fore.CYAN + f"\n🔍 Reading cookies from folder: {cookies_folder}")

        if not os.path.exists(cookies_folder):
            print(Fore.RED + "⚠️ Cookies folder not found!")
            input(Fore.YELLOW + "Press Enter to exit...")
            return

        txt_files = [f for f in os.listdir(cookies_folder) if f.endswith('.txt')]

        print(Fore.CYAN + f"Found {len(txt_files)} .txt files:")
        for f in txt_files:
            print(Fore.CYAN + f" - {f}")

        if not txt_files:
            print(Fore.RED + "⚠️ No .txt files found in the cookies folder.")
            input(Fore.YELLOW + "Press Enter to exit...")
            return

        valid_folder = os.path.join(script_dir, "valid")
        os.makedirs(valid_folder, exist_ok=True)

        valid_count = 0
        invalid_count = 0
        skipped_count = 0

        print(Fore.CYAN + "\n🔍 Checking cookies...\n")

        for file in tqdm(txt_files, desc="Processing", ncols=75, colour='blue'):
            filepath = os.path.join(cookies_folder, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    raw = f.read()

                format_type, data = detect_format(raw)
                if format_type == "json":
                    cookie_dict = convert_json_to_dict(data)
                elif format_type == "header":
                    cookie_dict = convert_header_string_to_dict(data)
                elif format_type == "netscape":
                    cookie_dict = convert_netscape_to_dict(data)
                else:
                    print(Fore.YELLOW + f"{file} ➜ SKIPPED ⚠️ (Unsupported format)")
                    skipped_count += 1
                    continue

                if is_cookie_valid(service, cookie_dict):
                    print(Fore.GREEN + f"{file} ➜ VALID ✅")
                    valid_count += 1
                    with open(os.path.join(valid_folder, file), 'w', encoding='utf-8') as vf:
                        vf.write(raw)
                else:
                    print(Fore.RED + f"{file} ➜ INVALID ❌")
                    invalid_count += 1
            except Exception as e:
                print(Fore.RED + f"{file} ➜ ERROR ❌ ({e})")
                invalid_count += 1

        print()
        print(Style.BRIGHT + Fore.CYAN + f"📊 Summary: {Fore.GREEN}{valid_count} Valid{Fore.CYAN}, {Fore.RED}{invalid_count} Invalid{Fore.CYAN}, {Fore.YELLOW}{skipped_count} Skipped")
        input(Fore.YELLOW + "\nPress Enter to return to menu...")

if __name__ == "__main__":
    main()
