import os
import re
import time
import subprocess
from ..utils.system import IS_WINDOWS, run_command
from ..ui.display import print_info, print_error, print_warning, Colors


def scan_networks(interface):
    """Scan for available WiFi networks"""
    print_info("Scanning for WiFi networks (this will take ~10 seconds)...")

    scan_file = "/tmp/wifi_scan" if not IS_WINDOWS else os.path.join(
        os.environ.get('TEMP', '.'), 'wifi_scan'
    )

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
            bssid      = parts[0].strip()
            channel    = parts[3].strip()
            encryption = parts[5].strip()
            power      = parts[8].strip()
            essid      = parts[13].strip()

            if not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', bssid):
                continue
            if not essid or 'WPA' not in encryption:
                continue
            if not channel.isdigit():
                continue

            networks.append({
                'bssid': bssid, 'channel': channel,
                'essid': essid, 'encryption': encryption, 'power': power
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


def select_network(networks):
    """Let user select a network"""
    while True:
        choice = input(
            f"{Colors.OKBLUE}Select network number (1-{len(networks)}) or 'r' to rescan: {Colors.ENDC}"
        ).strip().lower()
        if choice == 'r':
            return None
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(networks):
                selected = networks[choice_num - 1]
                from ..ui.display import print_success
                print_success(f"Selected: {selected['essid']} (Channel: {selected['channel']})")
                return selected
        print_error(f"Please enter a number between 1 and {len(networks)}, or 'r' to rescan")