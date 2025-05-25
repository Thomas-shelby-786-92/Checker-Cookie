import os
import json
import requests
from colorama import Fore, Style, init
from tqdm import tqdm

init(autoreset=True)

# Supported services
BASE_URLS = {
    "netflix": {"url": "https://www.netflix.com/browse", "domain": ".netflix.com"},
    "spotify": {"url": "https://open.spotify.com/", "domain": ".spotify.com"}
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

def display_menu():
    print(Style.BRIGHT + Fore.BLUE + "\n📁 Cookie Validator\n")
    print(Fore.BLUE + "1. Netflix")
    print(Fore.BLUE + "2. Spotify")
    print(Fore.BLUE + "3. Exit")
    print(Fore.CYAN + "\nChoose an option: ", end='')

def is_cookie_valid(service, cookie_dict):
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        session.cookies.update(cookie_dict)

        url = BASE_URLS[service]["url"]
        response = session.get(url, allow_redirects=False)

        return response.status_code in [200, 302]
    except:
        return False

def is_valid_cookie_format(cookie_data, domain_required):
    if not isinstance(cookie_data, list):
        return False
    return any(cookie.get("domain") == domain_required for cookie in cookie_data)

def convert_to_cookie_dict(cookie_data):
    return {c["name"]: c["value"] for c in cookie_data if "name" in c and "value" in c}

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        display_menu()
        choice = input().strip()

        if choice == '3':
            print(Fore.MAGENTA + "👋 Exiting... Goodbye!")
            break
        elif choice not in ['1', '2']:
            print(Fore.RED + "❌ Invalid option. Please try again.")
            input(Fore.YELLOW + "Press Enter to continue...")
            continue

        service = "netflix" if choice == '1' else "spotify"
        domain_required = BASE_URLS[service]['domain']

        base_path = os.getcwd()
        subdirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        if not subdirs:
            print(Fore.RED + "⚠️ No folder found to read cookies from.")
            input(Fore.YELLOW + "Press Enter to exit...")
            return

        first_folder = os.path.join(base_path, subdirs[0])
        txt_files = [f for f in os.listdir(first_folder) if f.endswith('.txt')]

        if not txt_files:
            print(Fore.RED + f"⚠️ No .txt files found in folder: {subdirs[0]}")
            input(Fore.YELLOW + "Press Enter to exit...")
            return

        valid_folder = os.path.join(base_path, "valid")
        os.makedirs(valid_folder, exist_ok=True)

        valid_count = 0
        invalid_count = 0
        skipped_count = 0

        print(Fore.CYAN + "\n🔍 Checking cookies...\n")

        for file in tqdm(txt_files, desc="Processing", ncols=75, colour='blue'):
            filepath = os.path.join(first_folder, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    cookie_data = json.load(f)

                if not is_valid_cookie_format(cookie_data, domain_required):
                    print(Fore.YELLOW + f"{file} ➜ SKIPPED ⚠️ (Not a {service} cookie)")
                    skipped_count += 1
                    continue

                cookie_dict = convert_to_cookie_dict(cookie_data)
                if is_cookie_valid(service, cookie_dict):
                    print(Fore.GREEN + f"{file} ➜ VALID ✅")
                    valid_count += 1
                    with open(os.path.join(valid_folder, file), 'w', encoding='utf-8') as vf:
                        json.dump(cookie_data, vf, indent=2)
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
