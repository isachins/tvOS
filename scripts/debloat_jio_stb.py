#!/usr/bin/env python3
"""
Jio Set-Top Box Debloat & Apple TV Launcher Assistant (Python Edition)
Cross-platform helper to connect, clean, debloat, and set custom launcher.
"""

import sys
import subprocess
import socket
import time

JIO_BLOATWARE = [
    ("com.jio.media.stblauncher", "Jio Default STB Home Launcher"),
    ("com.jio.jiolauncher", "Jio Secondary Launcher"),
    ("com.jio.media.ondemand", "Jio On-Demand Video Services"),
    ("com.jio.media.jionetworktools", "Jio Network Diagnostics / Telemetry"),
    ("com.jio.stb.telemetry", "Jio Background Telemetry Tracker"),
    ("com.jio.stb.adservice", "Jio STB System Ads & Promos"),
    ("com.jio.media.jiodrive", "Jio Cloud Drive"),
    ("com.jio.media.jioshop", "Jio Shopping App"),
    ("com.jio.media.jioexpress", "Jio Express Delivery")
]

def run_adb(cmd_args):
    try:
        res = subprocess.run(["adb"] + cmd_args, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        return None
    except FileNotFoundError:
        print("\n❌ Error: 'adb' command not found. Please install Android Platform Tools or run from Homebrew/Android Studio.")
        sys.exit(1)

def scan_local_stb():
    print("🔍 Scanning local subnet for Android TV / Jio STB with port 5555 open...")
    # Get local IP base
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        ip_parts = local_ip.split(".")
        subnet = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}."
    except Exception:
        subnet = "192.168.29."

    print(f"📡 Probing subnet {subnet}1 - {subnet}254 on port 5555 (timeout 100ms)...")
    found_ips = []
    for i in range(1, 255):
        test_ip = f"{subnet}{i}"
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.08)
        result = sock.connect_ex((test_ip, 5555))
        if result == 0:
            found_ips.append(test_ip)
            print(f"   🎯 Found active ADB device at: {test_ip}:5555")
        sock.close()

    return found_ips

def main():
    print("=" * 60)
    print("  🍎 Jio Set-Top Box Cleaner & Apple tvOS Setup Assistant")
    print("=" * 60)

    devices = run_adb(["devices"])
    connected = False
    if devices and "5555" in devices:
        print("✅ Already connected to ADB device via Wi-Fi!")
        connected = True

    if not connected:
        ip = input("\nEnter Jio STB IP address (or press Enter to scan network): ").strip()
        if not ip:
            discovered = scan_local_stb()
            if discovered:
                ip = discovered[0]
                print(f"Using discovered IP: {ip}")
            else:
                ip = input("No devices auto-discovered. Please enter IP manually: ").strip()

        if ip:
            print(f"\n🔌 Connecting to {ip}:5555...")
            run_adb(["disconnect"])
            out = run_adb(["connect", f"{ip}:5555"])
            print(out)
            print("👉 Check your TV screen to accept the USB Debugging authorization prompt!")
            time.sleep(2)

    print("\nSelect an action:")
    print("1) Safe Debloat: Disable Jio Launcher & Ads (Apple TV Ready)")
    print("2) Restore Jio Default Launcher (Undo Changes)")
    print("3) Sideload Apple TV Launcher APK")
    print("4) Set Apple TV as Default Home Screen")
    print("5) Launch Home Screen (Keyevent 3)")
    print("6) Exit")

    choice = input("\nEnter choice [1-6]: ").strip()

    if choice == "1":
        print("\n🗑️  Disabling Jio Bloatware safely...")
        for pkg, desc in JIO_BLOATWARE:
            res = run_adb(["shell", "pm", "disable-user", "--user", "0", pkg])
            status = "✅ Disabled" if res and "disabled" in res.lower() else "ℹ️ Already disabled / not present"
            print(f" - {pkg} ({desc}): {status}")
        print("\n✨ Debloat finished! Your Jio STB is now clean and fast.")

    elif choice == "2":
        print("\n🔄 Restoring Jio stock launcher...")
        run_adb(["shell", "pm", "enable", "com.jio.media.stblauncher"])
        run_adb(["shell", "pm", "enable", "com.jio.jiolauncher"])
        print("✅ Jio launcher restored.")

    elif choice == "3":
        apk_path = input("Enter path to Apple TV APK [default: appletv_launcher.apk]: ").strip() or "appletv_launcher.apk"
        print(f"📲 Installing {apk_path}...")
        res = run_adb(["install", "-r", apk_path])
        print(res)

    elif choice == "4":
        print("🏠 Setting com.appletv.launcher as default Home Activity...")
        res = run_adb(["shell", "cmd", "package", "set-home-activity", "com.appletv.launcher/.MainActivity"])
        print("✅ Done! Press Home on your remote to view Apple TV UI.")

    elif choice == "5":
        run_adb(["shell", "input", "keyevent", "3"])
        print("🏠 Home button triggered on TV.")

    print("\nDone! Have a great day.")

if __name__ == "__main__":
    main()
