import os
import urllib.request
import urllib.error
from ..utils.system import IS_WINDOWS, get_script_dir, get_actual_user_home
from ..ui.display import print_info, print_success, print_warning, print_error, Colors


def _download_wordlist(dest_path, download_url):
    """Download wordlist.txt from GitHub releases with a progress bar."""
    print_info(f"Downloading wordlist.txt from GitHub releases...")
    print_info(f"URL: {download_url}")

    try:
        def _progress(block_num, block_size, total_size):
            if total_size <= 0:
                print(f"{Colors.WARNING}  Downloaded {block_num * block_size / 1024:.1f} KB...{Colors.ENDC}", end='\r')
                return
            downloaded = block_num * block_size
            percent    = min(100, downloaded * 100 // total_size)
            filled     = percent // 2
            bar        = '█' * filled + '░' * (50 - filled)
            dl_mb      = downloaded / (1024 * 1024)
            tot_mb     = total_size / (1024 * 1024)
            print(
                f"\r  {Colors.OKBLUE}[{bar}] {percent}%  {dl_mb:.1f}/{tot_mb:.1f} MB{Colors.ENDC}",
                end='', flush=True
            )

        urllib.request.urlretrieve(download_url, dest_path, _progress)
        print()  # newline after progress bar

        file_size = os.path.getsize(dest_path) / (1024 * 1024)
        print_success(f"wordlist.txt downloaded successfully ({file_size:.1f} MB)")
        return True

    except urllib.error.HTTPError as e:
        print()
        print_error(f"Download failed – HTTP {e.code}: {e.reason}")
        print_info("You can download it manually from:")
        print_info("https://github.com/OTAKUWeBer/WiFi-BruteForce/releases")
        return False
    except urllib.error.URLError as e:
        print()
        print_error(f"Download failed – network error: {e.reason}")
        print_info("Check your internet connection and try again, or download manually from:")
        print_info("https://github.com/OTAKUWeBer/WiFi-BruteForce/releases")
        return False
    except Exception as e:
        print()
        print_error(f"Download failed: {e}")
        # Clean up partial file
        if os.path.exists(dest_path):
            try:
                os.remove(dest_path)
            except Exception:
                pass
        return False


def get_wordlist_path(download_url):
    """
    1. Use wordlist.txt next to this script if present (ask to confirm).
    2. If missing, offer to auto-download it from GitHub releases.
    3. If download is declined / fails, search common OS locations.
    4. Fall back to manual path entry.
    """
    script_dir    = get_script_dir()
    user_home     = get_actual_user_home()
    default_wordlist = os.path.join(script_dir, 'wordlist.txt')

    # ── 1. Default wordlist already present ──────────────────
    if os.path.exists(default_wordlist):
        try:
            file_size = os.path.getsize(default_wordlist) / (1024 * 1024)
            print_success(f"Default wordlist found: wordlist.txt ({file_size:.1f} MB)")
        except Exception:
            print_success("Default wordlist found: wordlist.txt")

        use_default = input(
            f"{Colors.OKBLUE}Use default wordlist.txt? (Y/n): {Colors.ENDC}"
        ).strip().lower()

        if use_default in ('', 'y', 'yes'):
            return default_wordlist
        # User wants a different one – fall through

    # ── 2. wordlist.txt is missing – offer auto-download ─────
    else:
        print_warning("wordlist.txt not found next to script.")
        print_info("A wordlist is required to crack the captured handshake.")
        print()
        print(f"  {Colors.OKGREEN}1.{Colors.ENDC} Auto-download wordlist.txt from GitHub releases  {Colors.WARNING}(recommended){Colors.ENDC}")
        print(f"  {Colors.OKGREEN}2.{Colors.ENDC} Use a different / existing wordlist on this machine")
        print()

        choice = input(f"{Colors.OKBLUE}Select option (1/2): {Colors.ENDC}").strip()

        if choice in ('', '1'):
            downloaded = _download_wordlist(default_wordlist, download_url)
            if downloaded:
                return default_wordlist
            print_warning("Falling back to manual wordlist selection...")
        else:
            print_info("Searching for existing wordlists on this machine...")

    # ── 3. Search common OS locations ────────────────────────
    if IS_WINDOWS:
        common_wordlists = [
            os.path.join(script_dir, 'rockyou.txt'),
            os.path.join(user_home, 'Downloads', 'rockyou.txt'),
            os.path.join(user_home, 'wordlists', 'rockyou.txt'),
            r'C:\tools\wordlists\rockyou.txt',
            r'C:\Users\Public\wordlists\rockyou.txt',
        ]
    else:
        common_wordlists = [
            '/usr/share/wordlists/rockyou.txt',
            '/usr/share/SecLists/Passwords/WiFi-WPA/probable-v2-wpa-top4800.txt',
            os.path.join(user_home, 'Downloads', 'rockyou.txt'),
            '/usr/share/wordlists/rockyou.txt.gz',
            os.path.join(user_home, 'wordlists', 'rockyou.txt'),
            os.path.join(script_dir, 'rockyou.txt'),
        ]

    found_wordlists = [wl for wl in common_wordlists if os.path.exists(wl)]

    if found_wordlists:
        print_success(f"Found {len(found_wordlists)} wordlist(s) on this machine:\n")
        for idx, wl in enumerate(found_wordlists, 1):
            try:
                file_size = os.path.getsize(wl) / (1024 * 1024)
                print(f"  {Colors.OKGREEN}{idx}.{Colors.ENDC} {wl}")
                print(f"      {Colors.WARNING}Size: {file_size:.1f} MB{Colors.ENDC}")
            except Exception:
                print(f"  {Colors.OKGREEN}{idx}.{Colors.ENDC} {wl}")

        print(f"\n  {Colors.OKGREEN}0.{Colors.ENDC} Enter custom path")

        while True:
            pick = input(f"\n{Colors.OKBLUE}Select wordlist (0-{len(found_wordlists)}): {Colors.ENDC}").strip()
            if pick.isdigit():
                pick_num = int(pick)
                if pick_num == 0:
                    break  # fall through to manual input
                elif 1 <= pick_num <= len(found_wordlists):
                    selected_wordlist = found_wordlists[pick_num - 1]
                    print_success(f"Selected: {selected_wordlist}")
                    return selected_wordlist
                else:
                    print_error(f"Please enter 0-{len(found_wordlists)}")
            else:
                print_error("Please enter a number")

    # ── 4. Manual / custom path ───────────────────────────────
    print_info("\nEnter the full path to your wordlist file.")
    if IS_WINDOWS:
        print(f"  Example: C:\\Users\\You\\Downloads\\rockyou.txt")
    else:
        print(f"  Example: /usr/share/wordlists/rockyou.txt  or  ~/Downloads/rockyou.txt")

    while True:
        wordlist_path = input(f"\n{Colors.OKBLUE}Enter wordlist path: {Colors.ENDC}").strip()
        wordlist_path = wordlist_path.strip('"\'')

        if not IS_WINDOWS and wordlist_path.startswith('~'):
            wordlist_path = wordlist_path.replace('~', user_home, 1)
        else:
            wordlist_path = os.path.expanduser(wordlist_path)

        if os.path.exists(wordlist_path):
            try:
                file_size = os.path.getsize(wordlist_path) / (1024 * 1024)
                print_success(f"Wordlist found: {file_size:.1f} MB")
            except Exception:
                print_success("Wordlist found")
            return wordlist_path

        print_error(f"File not found: {wordlist_path}")
        retry = input(f"{Colors.WARNING}Try again? (y/n): {Colors.ENDC}").strip().lower()
        if retry != 'y':
            print_warning("Skipping password cracking (no wordlist selected)")
            return None