import os
import sys
import subprocess
from pathlib import Path

# Windows compatibility: only import pwd on Unix
IS_WINDOWS = os.name == 'nt'
if not IS_WINDOWS:
    import pwd


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
        return 1, None, str(e)
    except Exception as e:
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
    """Return the directory where the main script lives (root directory)"""
    # Get the directory containing main.py (go up from src/utils/system.py to root)
    current_file = os.path.abspath(__file__)
    src_dir = os.path.dirname(os.path.dirname(current_file))  # Go up to src/
    root_dir = os.path.dirname(src_dir)  # Go up to root directory
    return root_dir


def check_root():
    """Check for admin / root privileges"""
    if IS_WINDOWS:
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                from ..ui.display import print_error, print_info
                print_error("This script must be run as Administrator!")
                print_info("Right-click the terminal and choose 'Run as administrator'")
                sys.exit(1)
        except Exception:
            from ..ui.display import print_warning
            print_warning("Could not verify admin rights – continuing anyway")
    else:
        if os.geteuid() != 0:
            from ..ui.display import print_error, print_info
            print_error("This script must be run as root!")
            print_info("Please run: sudo python3 main.py")
            sys.exit(1)
    from ..ui.display import print_success
    print_success("Running with elevated privileges")


def check_dependencies():
    """Check if required tools are installed"""
    from ..ui.display import print_info, print_warning, print_error, print_success
    
    print_info("Checking dependencies...")

    if IS_WINDOWS:
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
    HAS_HASHCAT  = subprocess.run([which_cmd, 'hashcat'],       capture_output=True).returncode == 0
    HAS_HCXTOOLS = subprocess.run([which_cmd, 'hcxpcapngtool'], capture_output=True).returncode == 0

    if HAS_HASHCAT and HAS_HCXTOOLS:
        print_success("GPU cracking available (hashcat)")
    else:
        print_warning("GPU cracking not available (CPU only)")

    return HAS_HASHCAT, HAS_HCXTOOLS