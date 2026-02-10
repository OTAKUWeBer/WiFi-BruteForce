# WEBER – WiFi BruteForce Tool

> ⚠️ **For educational and authorized penetration testing use only.**  
> Do not use this tool on networks you do not own or have explicit written permission to test. Unauthorized access to computer networks is illegal.

---

## Features

- Auto-detects wireless interfaces
- Scans and lists nearby WPA/WPA2 networks
- Automatic handshake capture with deauth injection
- CPU cracking via `aircrack-ng`
- GPU cracking via `hashcat` (if available)
- Cross-platform: **Linux** and **Windows** (see notes)

---

## Installation Guide

### 🐧 Linux (Recommended)

#### 1. Update package lists

```bash
sudo apt update
```

#### 2. Install aircrack-ng suite

```bash
sudo apt install aircrack-ng
```

This installs all four tools the script needs:

| Tool | Purpose |
|------|---------|
| `airmon-ng` | Enable / disable monitor mode |
| `airodump-ng` | Capture packets and scan networks |
| `aireplay-ng` | Send deauth packets to trigger handshake |
| `aircrack-ng` | CPU-based WPA password cracking |

#### 3. Install supporting tools

```bash
sudo apt install iw wireless-tools
```

#### 4. Optional – GPU cracking (much faster)

```bash
sudo apt install hashcat hcxtools
```

`hcxtools` converts `.cap` files to hashcat's `.22000` format.  
`hashcat` then cracks using your GPU.

#### 5. Verify everything is installed

```bash
which airmon-ng airodump-ng aireplay-ng aircrack-ng
```

All four paths should print without errors.

#### Kali Linux / Parrot OS

These distros ship with aircrack-ng pre-installed. Just run:

```bash
sudo apt update && sudo apt install aircrack-ng iw wireless-tools
```

---

### 🪟 Windows

> **Note:** The aircrack-ng suite is primarily designed for Linux. Native Windows support is limited and some features (monitor mode, deauth) depend heavily on your adapter and driver.  
> For the best experience, use **Option A: WSL** or **Option B: Kali VM**.

---

#### Option A – WSL (Windows Subsystem for Linux) ✅ Recommended

WSL lets you run a full Linux environment inside Windows without a VM.

**Step 1 – Enable WSL**

Open PowerShell as Administrator and run:

```powershell
wsl --install
```

Restart your PC when prompted. This installs Ubuntu by default.

**Step 2 – Open the Ubuntu terminal and install tools**

```bash
sudo apt update
sudo apt install aircrack-ng iw wireless-tools hashcat hcxtools python3
```

**Step 3 – Pass your USB WiFi adapter into WSL**

WSL 2 does not have direct USB access by default. Use [usbipd-win](https://github.com/dorssel/usbipd-win):

```powershell
# In PowerShell (Admin)
winget install usbipd

# List connected USB devices
usbipd list

# Attach your WiFi adapter — replace X-Y with your device's bus ID
usbipd attach --wsl --busid X-Y
```

**Step 4 – Run the script inside WSL**

```bash
sudo python3 main.py
```

---

#### Option B – Kali Linux VM

1. Download [Kali Linux](https://www.kali.org/get-kali/#kali-virtual-machines) (pre-built VirtualBox / VMware image)
2. Import into [VirtualBox](https://www.virtualbox.org/) or VMware
3. In VM settings → **USB** → add your WiFi adapter as a USB passthrough device
4. Boot Kali — aircrack-ng is pre-installed
5. Run:

```bash
sudo python3 main.py
```

---

#### Option C – Native Windows (Limited)

> ⚠️ Monitor mode and deauth injection rarely work on native Windows. Most chipsets are unsupported. Only attempt this if your adapter has a confirmed compatible Windows driver.

**Step 1 – Install Python**

Download from [python.org](https://www.python.org/downloads/windows/) and run the installer.  
✅ Check **"Add Python to PATH"** before clicking Install.

**Step 2 – Install aircrack-ng for Windows**

Download the latest Windows build from [aircrack-ng.org/downloads](https://www.aircrack-ng.org/downloads.html) and run the installer.

**Step 3 – Add aircrack-ng to PATH**

1. Open **Start** → search **"Edit the system environment variables"**
2. Click **Environment Variables**
3. Under **System Variables** → select `Path` → click **Edit**
4. Click **New** and add the aircrack-ng bin folder, e.g.:
   ```
   C:\Program Files\Aircrack-ng\bin
   ```
5. Click **OK** on all dialogs

**Step 4 – Verify**

Open a **new** PowerShell window and run:

```powershell
aircrack-ng --version
python --version
```

Both should print version numbers without errors.

**Step 5 – Run as Administrator**

Right-click **PowerShell** → **Run as Administrator**, then:

```powershell
python main.py
```

---

#### Optional – hashcat on Windows (GPU cracking)

1. Download from [hashcat.net/hashcat](https://hashcat.net/hashcat/) and extract to `C:\tools\hashcat\`
2. Add `C:\tools\hashcat\` to your system PATH (same steps as above)
3. Install GPU drivers:
   - **NVIDIA:** [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
   - **AMD:** [ROCm / OpenCL drivers](https://www.amd.com/en/support)
4. Verify:
   ```powershell
   hashcat -I
   ```
   You should see your GPU listed under OpenCL or CUDA devices.

---

## Clone the Repo

```bash
git clone https://github.com/OTAKUWeBer/WiFi-BruteForce
cd WiFi-BruteForce
```

No additional Python packages are required — only the standard library is used.

---

## Wordlist

A curated `wordlist.txt` is included in the **[Releases](https://github.com/OTAKUWeBer/WiFi-BruteForce/releases)** page.

Download it and place it in the **same folder as `main.py`**:

```
WiFi-BruteForce/
├── main.py
└── wordlist.txt   ← place here
```

When you run the tool, it will automatically detect `wordlist.txt` and ask if you want to use it.  
You can also choose a different wordlist (e.g. `rockyou.txt`) or enter a custom path at the prompt.

Common wordlist locations the tool also checks automatically:

| OS | Path |
|----|------|
| Linux | `/usr/share/wordlists/rockyou.txt` |
| Linux | `/usr/share/SecLists/Passwords/WiFi-WPA/probable-v2-wpa-top4800.txt` |
| Windows | `C:\tools\wordlists\rockyou.txt` |
| Windows | `%USERPROFILE%\Downloads\rockyou.txt` |

---

## Usage

### Linux

```bash
sudo python3 main.py
```

### Windows (Administrator terminal)

```powershell
python main.py
```

---

## How It Works

The tool walks you through 5 steps automatically:

```
Step 1 → Detect / select wireless interface
Step 2 → Enable monitor mode, scan for WPA/WPA2 networks, select target
Step 3 → Select wordlist (defaults to wordlist.txt)
Step 4 → Capture WPA handshake (auto deauth loop, up to 20 attempts)
Step 5 → Crack password (GPU via hashcat if available, otherwise CPU via aircrack-ng)
```

Captured `.cap` files are saved to `./wifi_captures/`.

---

## Troubleshooting

**Handshake not captured after 20 attempts**
- Ensure at least one client device is actively connected to the target network
- Move closer to the access point
- Some adapters don't support injection — test with `aireplay-ng --test <interface>`

**Monitor mode fails**
- Run `sudo airmon-ng check kill` manually to stop conflicting processes (NetworkManager, wpa_supplicant)
- Some USB adapters require external drivers, e.g. for Realtek chipsets:
  ```bash
  sudo apt install dkms
  git clone https://github.com/aircrack-ng/rtl8812au
  cd rtl8812au && sudo make && sudo make install
  ```

**`iw` / `iwconfig` not found**

```bash
sudo apt install iw wireless-tools
```

**Permission denied on Linux**

The script must be run as root:

```bash
sudo python3 main.py
```

**ANSI colors not showing on Windows**
- Use **Windows Terminal** or **PowerShell 7+** — the tool enables ANSI automatically
- Avoid the legacy `cmd.exe` console

**WSL can't see the WiFi adapter**
- Make sure you used `usbipd attach --wsl --busid X-Y` with the correct bus ID
- Run `lsusb` inside WSL to confirm the device is visible

---

## File Structure

```
WiFi-BruteForce/
├── main.py          # Main script
├── wordlist.txt     # Default wordlist (download from Releases)
├── README.md
└── wifi_captures/   # Created automatically on first run
    └── capture_<ESSID>_<timestamp>-01.cap
```

---

## Legal Notice

This tool is intended **only** for:
- Testing your own networks
- Authorized security assessments (with written permission)
- Educational and research purposes in controlled lab environments

The author assumes **no liability** for misuse. Always comply with applicable laws in your jurisdiction.