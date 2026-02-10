"""
Configuration constants for WiFi BruteForce Tool
"""

# GitHub release URL for wordlist.txt
WORDLIST_DOWNLOAD_URL = (
    "https://github.com/OTAKUWeBer/WiFi-BruteForce/releases/latest/download/wordlist.txt"
)

# Capture directory
CAPTURE_DIR = './wifi_captures'

# Maximum handshake capture attempts
MAX_HANDSHAKE_ATTEMPTS = 20

# Scan duration in seconds
SCAN_DURATION = 10

# Deauth packet count
DEAUTH_PACKET_COUNT = 5

# Wait time between deauth attempts (seconds)
DEAUTH_WAIT_TIME = 8

# Airodump startup wait time (seconds)
AIRODUMP_STARTUP_WAIT = 3

# Process termination wait time (seconds)
PROCESS_TERMINATION_WAIT = 2