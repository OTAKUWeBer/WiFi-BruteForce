import os
import subprocess
import sys


class Colors:
    """ANSI color codes for terminal output"""
    HEADER    = '\033[95m'
    OKBLUE    = '\033[94m'
    OKCYAN    = '\033[96m'
    OKGREEN   = '\033[92m'
    WARNING   = '\033[93m'
    FAIL      = '\033[91m'
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'
    MAGENTA   = '\033[35m'


def clear_screen():
    """Clear terminal screen (cross-platform)"""
    if os.name == 'nt':
        subprocess.run(['cmd', '/c', 'cls'], shell=False)
    else:
        subprocess.run(['clear'])


def enable_ansi_windows():
    """Enable ANSI escape codes on Windows 10+"""
    if os.name == 'nt':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass


def print_banner():
    """Display application banner"""
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
    """Print success message with checkmark"""
    print(f"{Colors.OKGREEN}[✓] {message}{Colors.ENDC}")


def print_error(message):
    """Print error message with cross"""
    print(f"{Colors.FAIL}[✗] {message}{Colors.ENDC}")


def print_info(message):
    """Print info message with info icon"""
    print(f"{Colors.OKBLUE}[i] {message}{Colors.ENDC}")


def print_warning(message):
    """Print warning message with exclamation"""
    print(f"{Colors.WARNING}[!] {message}{Colors.ENDC}")


def print_step(step_num, total_steps, message):
    """Print step indicator"""
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
                signal_color, signal = Colors.OKGREEN, "Excellent"
            elif power_val >= -60:
                signal_color, signal = Colors.OKGREEN, "Good"
            elif power_val >= -70:
                signal_color, signal = Colors.WARNING, "Fair"
            else:
                signal_color, signal = Colors.FAIL, "Weak"
        except Exception:
            signal_color, signal = Colors.ENDC, "Unknown"

        essid = net['essid'][:28] if len(net['essid']) > 28 else net['essid']
        print(
            f"{Colors.OKBLUE}{idx:<5}{Colors.ENDC} {essid:<30} "
            f"{signal_color}{signal:<10}{Colors.ENDC} {net['channel']:<10} {net['encryption']:<15}"
        )

    print()
    return networks


def display_completion():
    """Display completion message"""
    print(f"\n{Colors.BOLD}═══════════════════════════════════════════════════════════{Colors.ENDC}")
    print(f"{Colors.BOLD}                      CLEANUP{Colors.ENDC}")
    print(f"{Colors.BOLD}═══════════════════════════════════════════════════════════{Colors.ENDC}\n")

    print(f"\n{Colors.OKGREEN}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║                    All Done! ✓                           ║")
    print("║         Thank you for using WiFi Testing Tool            ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")