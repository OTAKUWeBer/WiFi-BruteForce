import os
import re
from ..utils.system import run_command
from ..ui.display import print_info, print_success, print_warning, print_error, display_cracked_password


def check_gpu_available():
    """Check if GPU is available for hashcat"""
    print_info("Checking GPU availability...")
    returncode, stdout, _ = run_command(['hashcat', '-I'], capture_output=True)
    if returncode == 0 and stdout and ('CUDA' in stdout or 'OpenCL' in stdout):
        print_success("GPU detected - using GPU acceleration")
        return True
    print_warning("No GPU detected - using CPU mode")
    return False


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

    returncode, _, _ = run_command(['hashcat', '-m', '22000', '-D', '2', hash_file, wordlist])

    if returncode == 0:
        returncode_show, stdout_show, _ = run_command(
            ['hashcat', '-m', '22000', hash_file, '--show'], capture_output=True
        )
        if stdout_show:
            for line in stdout_show.strip().split('\n'):
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) >= 5:
                        display_cracked_password(parts[-2], parts[-1])
                        break
        print_info("\nRaw hashcat output:")
        from ..ui.display import Colors
        print(f"{Colors.WARNING}{stdout_show}{Colors.ENDC}")
        return True

    print_warning("\n❌ Password not found in wordlist")
    print_info("Try a different/larger wordlist")
    return False


def crack_with_aircrack(cap_file, wordlist):
    """Crack password using aircrack-ng (CPU)"""
    print_success("Starting CPU cracking...")
    print_warning("This may take a while depending on wordlist size\n")

    returncode, stdout, _ = run_command(['aircrack-ng', cap_file, '-w', wordlist], capture_output=True)

    if returncode == 0:
        essid    = None
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
            from ..ui.display import Colors
            print(f"\n{Colors.WARNING}{stdout}{Colors.ENDC}")
        return True

    print_warning("\n❌ Password not found in wordlist")
    print_info("Try a different/larger wordlist")
    return False