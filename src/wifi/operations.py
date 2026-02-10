import os
import re
import sys
import time
import subprocess
from ..utils.system import IS_WINDOWS, run_command
from ..ui.display import print_info, print_error, print_success, print_warning


def get_wireless_interface():
    """Detect wireless interface (cross-platform)"""
    print_info("Detecting wireless interface...")

    if IS_WINDOWS:
        returncode, stdout, _ = run_command(
            ['netsh', 'wlan', 'show', 'interfaces'], capture_output=True
        )
        if returncode != 0 or not stdout:
            print_error("Could not detect wireless interface via netsh")
            sys.exit(1)
        interfaces = [i.strip() for i in re.findall(r'Name\s*:\s*(.+)', stdout)]
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

    print_success(f"Found {len(interfaces)} wireless interfaces:")
    from ..ui.display import Colors
    for idx, iface in enumerate(interfaces, 1):
        print(f"  {Colors.OKGREEN}{idx}.{Colors.ENDC} {iface}")

    while True:
        choice = input(f"\n{Colors.OKBLUE}Select interface (1-{len(interfaces)}): {Colors.ENDC}").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(interfaces):
            selected = interfaces[int(choice) - 1]
            print_success(f"Selected: {selected}")
            return selected
        print_error(f"Please enter a number between 1 and {len(interfaces)}")


def enable_monitor_mode(interface):
    """Enable monitor mode on wireless interface (Linux only)"""
    if IS_WINDOWS:
        print_warning("Monitor mode is managed by the adapter driver on Windows.")
        print_info("Ensure your adapter supports monitor mode and switch it manually if needed.")
        return interface

    print_info("Enabling monitor mode...")
    print_warning("This will disconnect your internet temporarily")

    run_command(['airmon-ng', 'check', 'kill'], capture_output=True)
    returncode, _, _ = run_command(['airmon-ng', 'start', interface], capture_output=True)

    if returncode != 0:
        print_error("Failed to enable monitor mode")
        sys.exit(1)

    time.sleep(2)
    possible_names = [f"{interface}mon", "wlan0mon", "wlan1mon", "wlan2mon", interface]
    returncode_iw, stdout_iw, _ = run_command(['iwconfig'], capture_output=True)

    monitor_interface = None
    if returncode_iw == 0 and stdout_iw:
        for line in stdout_iw.split('\n'):
            if 'Mode:Monitor' in line:
                monitor_interface = line.split()[0]
                break

    if not monitor_interface:
        for name in possible_names:
            ret, out, _ = run_command(['iw', 'dev', name, 'info'], capture_output=True)
            if ret == 0 and out and 'type monitor' in out.lower():
                monitor_interface = name
                break

    if not monitor_interface:
        monitor_interface = f"{interface}mon"

    print_success(f"Monitor mode enabled: {monitor_interface}")
    return monitor_interface


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
    returncode, stdout, _ = run_command(['aircrack-ng', cap_file], capture_output=True)
    if not stdout:
        return False

    # aircrack-ng reports "(1 handshake)" when valid — "0 handshake" is a false positive
    # Match lines like: "C0:06:C3:EA:B2:38  MyNetwork  WPA (1 handshake)"
    for line in stdout.splitlines():
        if bssid.lower() in line.lower():
            match = re.search(r'\((\d+)\s+handshake', line, re.IGNORECASE)
            if match and int(match.group(1)) > 0:
                return True

    return False