#!/usr/bin/env python3
"""
CleanYourTV One-Click Installer for Mi TV Stick / Xiaomi Android TV
Powered by Gathin23/cleanyourtv + upstream launcher v2.5.0
"""

import os
import sys
import subprocess
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
VENV_PY = os.path.join(PROJECT_ROOT, "tools", "venv", "bin", "python3")
TV_PY = os.path.join(PROJECT_ROOT, "tools", "tv.py")
LAUNCHER_APK = os.path.join(PROJECT_ROOT, "cleanyourtv-launcher.apk")
ADB_BIN = os.path.join(PROJECT_ROOT, "platform-tools", "adb")
BACKUP_DIR = os.path.join(PROJECT_ROOT, "backup")

def run_tv_cmd(tv_ip, cmd_args):
    """Run tv.py using the dedicated virtualenv (no external adb binary needed)."""
    env = os.environ.copy()
    env["TV_HOST"] = tv_ip
    full_cmd = [VENV_PY, "-I", TV_PY] + cmd_args
    res = subprocess.run(full_cmd, env=env, capture_output=True, text=True)
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def main():
    print("=" * 64)
    print("  🍎 CleanYourTV — Apple TV Home Screen for Mi TV Stick")
    print("  Repository: https://github.com/Gathin23/cleanyourtv")
    print("=" * 64)

    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print("\nUsage:")
        print("  python3 scripts/install_mistick.py <MI_TV_STICK_IP>")
        print("Example:")
        print("  python3 scripts/install_mistick.py 192.168.1.113\n")
        sys.exit(0)

    # 1. Ask for TV IP
    tv_ip = os.environ.get("TV_HOST")
    if not tv_ip:
        if len(sys.argv) > 1:
            tv_ip = sys.argv[1].strip()
        else:
            tv_ip = input("\n👉 Enter your Mi TV Stick IP address (e.g. 192.168.1.113): ").strip()

    if not tv_ip:
        print("❌ Error: TV IP address is required.")
        sys.exit(1)

    print(f"\n🔍 Probing Mi TV Stick at {tv_ip}:5555 over Wi-Fi...")
    print("👉 If prompted on your TV screen, check 'Always allow from this computer' and click OK!")
    
    stdout, stderr, code = run_tv_cmd(tv_ip, ["--probe"])
    if code != 0:
        print(f"⚠️ Initial probe response:\n{stdout}\n{stderr}")
        print("\nRetrying in 3 seconds (make sure USB Debugging is ON in Developer options)...")
        time.sleep(3)
        stdout, stderr, code = run_tv_cmd(tv_ip, ["--probe"])

    print(f"✅ TV Response:\n{stdout}")

    # 2. Backup current state
    os.makedirs(BACKUP_DIR, exist_ok=True)
    print(f"\n📦 Backing up installed packages to {BACKUP_DIR}/packages.txt...")
    pkg_list, _, _ = run_tv_cmd(tv_ip, ["pm", "list", "packages"])
    with open(os.path.join(BACKUP_DIR, "packages.txt"), "w") as f:
        f.write(pkg_list)

    # 3. Debloat Xiaomi PatchWall & Telemetry
    print("\n🧹 Step 1: Debloating Xiaomi PatchWall & Telemetry (Safe Disable)...")
    xiaomi_packages = [
        "com.mitv.tvhome",
        "com.mitv.tvhome.atv",
        "com.mitv.tvhome.michannel",
        "com.miui.tv.analytics",
        "com.xiaomi.mitv.advert",
        "com.xm.webcontent",
        "tv.alphonso.alphonso_eula",
        "com.google.android.tvrecommendations",
        "com.mitv.screensaver"
    ]

    for pkg in xiaomi_packages:
        print(f"   - Disabling {pkg}...", end=" ", flush=True)
        out, err, ret = run_tv_cmd(tv_ip, ["pm", "disable-user", "--user", "0", pkg])
        if "disabled" in out.lower() or "new state: disabled" in out.lower():
            print("DONE ✅")
        else:
            print("SKIPPED / ALREADY OFF")

    # 4. Install CleanYourTV Launcher APK
    print(f"\n📲 Step 2: Installing CleanYourTV Apple TV Launcher APK...")
    res = subprocess.run([ADB_BIN, "-s", f"{tv_ip}:5555", "install", "-r", LAUNCHER_APK], capture_output=True, text=True)
    print(f"   Result: {res.stdout.strip() or res.stderr.strip()}")

    # 5. Set as Default Home Screen
    print("\n🏠 Step 3: Setting CleanYourTV as Default Home Screen Activity...")
    subprocess.run([ADB_BIN, "-s", f"{tv_ip}:5555", "shell", "pm", "grant", "com.gathin.tvhome", "android.permission.ACCESS_FINE_LOCATION"], capture_output=True)
    subprocess.run([ADB_BIN, "-s", f"{tv_ip}:5555", "shell", "cmd", "package", "compile", "-m", "speed", "-f", "com.gathin.tvhome"], capture_output=True)
    subprocess.run([ADB_BIN, "-s", f"{tv_ip}:5555", "shell", "cmd", "package", "set-home-activity", "--user", "0", "com.gathin.tvhome/.MainActivity"], capture_output=True)
    subprocess.run([ADB_BIN, "-s", f"{tv_ip}:5555", "shell", "pm", "disable-user", "--user", "0", "com.google.android.tvlauncher"], capture_output=True)
    
    # 6. Press Home Button
    print("👉 Triggering Home keyevent on TV...")
    subprocess.run([ADB_BIN, "-s", f"{tv_ip}:5555", "shell", "input", "keyevent", "3"], capture_output=True)

    print("\n" + "=" * 64)
    print("🎉 SUCCESS! CleanYourTV is now active on your Mi TV Stick!")
    print("🍎 Enjoy your pitch-black, fluid Apple TV-style home screen.")
    print("=" * 64)

if __name__ == "__main__":
    main()
