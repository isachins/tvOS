#!/usr/bin/env bash
# ==============================================================================
# Jio Set-Top Box (JHS C200 / JHSD200) Safe Debloat & Apple TV Launcher Setup
# ==============================================================================
# Usage:
#   chmod +x debloat_jio_stb.sh
#   ./debloat_jio_stb.sh <JIO_STB_IP_ADDRESS>
# Example:
#   ./debloat_jio_stb.sh 192.168.29.150
# ==============================================================================

set -e

STB_IP="${1}"
PORT="5555"

echo "=========================================================="
echo "  🍎 Jio Set-Top Box Debloater & Apple tvOS Installer"
echo "=========================================================="

if [ -z "$STB_IP" ]; then
    echo "⚠️  No IP provided. Enter your Jio STB IP address (e.g. 192.168.29.150):"
    read -r STB_IP
fi

echo "🔍 Connecting to Jio STB at ${STB_IP}:${PORT}..."
adb disconnect >/dev/null 2>&1 || true
adb connect "${STB_IP}:${PORT}"

echo "⏳ Waiting for ADB authorization on TV..."
echo "👉 Check your TV screen right now and select 'Always allow from this computer' -> OK!"
adb wait-for-device

DEVICE_MODEL=$(adb shell getprop ro.product.model 2>/dev/null || echo "Android TV Device")
echo "✅ Connected to: ${DEVICE_MODEL}"
echo ""

echo "----------------------------------------------------------"
echo "📋 Step 1: Disabling Jio Stock Bloatware & Default Launcher..."
echo "----------------------------------------------------------"

# List of Jio packages to safely disable without breaking Wi-Fi, Bluetooth, HDMI, or Remotes
JIO_PACKAGES=(
    "com.jio.media.stblauncher"
    "com.jio.jiolauncher"
    "com.jio.media.ondemand"
    "com.jio.media.jionetworktools"
    "com.jio.stb.telemetry"
    "com.jio.stb.adservice"
    "com.jio.media.jiodrive"
    "com.jio.media.jioshop"
    "com.jio.media.jioexpress"
)

for pkg in "${JIO_PACKAGES[@]}"; do
    echo -n "   Disabling ${pkg}... "
    adb shell pm disable-user --user 0 "$pkg" 2>/dev/null && echo "DONE ✅" || echo "SKIPPED (Not found or already disabled)"
done

echo ""
echo "----------------------------------------------------------"
echo "📲 Step 2: Sideloading App Stores (Aurora Store / Google Play Client)..."
echo "----------------------------------------------------------"
if [ -f "aurora_store_tv.apk" ]; then
    echo "   Installing Aurora Store (Google Play Store client for TV)..."
    adb install -r -d "aurora_store_tv.apk"
    echo "   ✅ Aurora Store installed!"
else
    echo "   ℹ️  No local aurora_store_tv.apk found. You can install it from https://auroraoss.com"
fi

if [ -f "button_mapper.apk" ]; then
    echo "   Installing Button Mapper for Jio Remote..."
    adb install -r -d "button_mapper.apk"
    echo "   ✅ Button Mapper installed!"
fi

echo ""
echo "----------------------------------------------------------"
echo "🏠 Step 3: Setting Default Home Launcher..."
echo "----------------------------------------------------------"
# If our Apple TV launcher APK exists, install and set it
if [ -f "appletv_launcher.apk" ]; then
    echo "   Installing Apple TV Launcher APK..."
    adb install -r "appletv_launcher.apk"
    adb shell cmd package set-home-activity com.appletv.launcher/.MainActivity
    echo "   ✅ Apple TV Launcher is now your default Home screen!"
else
    echo "   ℹ️  To set Apple TV Launcher as default once built:"
    echo "      adb shell cmd package set-home-activity com.appletv.launcher/.MainActivity"
fi

echo ""
echo "----------------------------------------------------------"
echo "🎉 DEBLOAT COMPLETE! Pressing Home on your TV..."
echo "----------------------------------------------------------"
adb shell input keyevent 3

echo "✨ Enjoy your clean, bloat-free Apple TV experience on Jio STB!"
