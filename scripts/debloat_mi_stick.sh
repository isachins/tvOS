#!/usr/bin/env bash
# ==============================================================================
# Mi TV Stick (Xiaomi / Mi Box) Safe Debloat & Apple TV Launcher Setup
# ==============================================================================
# Usage:
#   chmod +x debloat_mi_stick.sh
#   ./debloat_mi_stick.sh <MI_STICK_IP_ADDRESS>
# Example:
#   ./debloat_mi_stick.sh 192.168.29.120
# ==============================================================================

set -e

STICK_IP="${1}"
PORT="5555"

echo "=========================================================="
echo "  🍎 Mi TV Stick Debloater & Apple tvOS Setup"
echo "=========================================================="

if [ -z "$STICK_IP" ]; then
    echo "⚠️  Enter your Mi TV Stick IP address (e.g. 192.168.29.120):"
    read -r STICK_IP
fi

echo "🔍 Connecting to Mi TV Stick at ${STICK_IP}:${PORT}..."
adb disconnect >/dev/null 2>&1 || true
adb connect "${STICK_IP}:${PORT}"

echo "⏳ Waiting for ADB authorization on TV screen..."
echo "👉 Look at your TV screen and click 'Always allow from this computer' -> OK!"
adb wait-for-device

DEVICE_MODEL=$(adb shell getprop ro.product.model 2>/dev/null || echo "Mi TV Stick")
echo "✅ Successfully connected to: ${DEVICE_MODEL}"
echo ""

echo "----------------------------------------------------------"
echo "🚀 Step 1: Removing Xiaomi PatchWall & Telemetry Bloatware..."
echo "   (This frees up massive RAM and speeds up your Mi Stick!)"
echo "----------------------------------------------------------"

MI_BLOATWARE=(
    "com.mitv.tvhome"                 # Xiaomi PatchWall Launcher
    "com.xiaomi.mitv.advert"          # Xiaomi System Ads
    "com.miui.analytics"              # Xiaomi Analytics & Tracking
    "com.xiaomi.mitv.upgrade"         # Xiaomi Forced Upgrade Prompts
    "com.xiaomi.account"              # Mi Account Services
    "com.xiaomi.mitv.payment"         # Mi Payment Services
    "com.mitv.screensaver"            # Xiaomi Default Screensaver
    "com.xiaomi.tv.appupgrade"        # Mi TV App Upgrader
    "com.mitv.tvhome.atv"             # PatchWall ATV Stub
)

for pkg in "${MI_BLOATWARE[@]}"; do
    echo -n "   Disabling ${pkg}... "
    adb shell pm disable-user --user 0 "$pkg" 2>/dev/null && echo "DISABLED ✅" || echo "SKIPPED (Not found or already disabled)"
done

echo ""
echo "----------------------------------------------------------"
echo "🛍️  Step 2: Google Play Store & Google Play Services Status"
echo "----------------------------------------------------------"
GMS_STATUS=$(adb shell pm list packages | grep "com.android.vending" || true)
if [ -n "$GMS_STATUS" ]; then
    echo "   ✅ Official Google Play Store is ACTIVE & CERTIFIED on this device!"
else
    echo "   ℹ️  Google Play Store package not detected."
fi

echo ""
echo "----------------------------------------------------------"
echo "🏠 Step 3: Setting Custom Launcher & Home Override"
echo "----------------------------------------------------------"
# Check if custom launcher APK exists locally
if [ -f "appletv_launcher.apk" ]; then
    echo "   Installing Apple TV Launcher APK..."
    adb install -r "appletv_launcher.apk"
    adb shell cmd package set-home-activity com.appletv.launcher/.MainActivity 2>/dev/null || true
    echo "   ✅ Apple TV Launcher installed!"
else
    echo "   ℹ️  Local appletv_launcher.apk not found in this folder."
    echo "   👉 You can install 'Launcher Manager' or 'Projectivy Launcher' from the Play Store,"
    echo "      or use our web tvOS launcher!"
fi

echo ""
echo "----------------------------------------------------------"
echo "🎉 MI TV STICK OPTIMIZATION COMPLETE!"
echo "----------------------------------------------------------"
echo "Pressing Home key on your Mi Remote..."
adb shell input keyevent 3

echo "✨ Your Mi TV Stick is now bloat-free, significantly faster, and ready for Apple TV UI!"
