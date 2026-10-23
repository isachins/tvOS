#!/usr/bin/env bash
set -e

TV_IP="${1:-192.168.1.113}"
PORT="5555"

echo "=========================================================="
echo "  🚀 Mi TV Stick Deep Debloater & Performance Optimizer"
echo "  Target: ${TV_IP}:${PORT}"
echo "=========================================================="

./platform-tools/adb connect "${TV_IP}:${PORT}"

TARGET_PACKAGES=(
    # --- User-Requested Apps ---
    "com.google.android.music"
    "com.google.android.play.games"
    "com.google.android.videos"
    "com.google.android.tv"
    "com.android.gallery3d"
    "com.google.android.apps.nbu.smartconnect.tv"
    "mitv.service"

    # --- Hardware Stubs (No Camera, No Printer, No NFC, No Cellular, No External Storage) ---
    "com.android.camera2"
    "com.android.printspooler"
    "com.android.se"
    "com.android.smspush"
    "com.android.externalstorage"
    "com.android.companiondevicemanager"
    "com.android.wallpapercropper"
    "com.android.htmlviewer"

    # --- Accessibility & Screen Reader (Unless visually impaired) ---
    "com.google.android.marvin.talkback"
    "com.google.android.tts"

    # --- Telemetry, Bug Reporting & Partner Bloat ---
    "com.miui.tv.analytics"
    "com.google.android.feedback"
    "com.google.android.tv.bugreportsender"
    "com.xiaomo.tv.milegal"
    "com.xiaomi.android.tvsetup.partnercustomizer"
    "android.autoinstalls.config.xiaomi.mibox3"
    "android.autoinstalls.config.xioami.mibox3"
    "com.android.cts.ctsshim"
    "com.android.cts.priv.ctsshim"

    # --- Unused Sync & Backup Stubs ---
    "com.android.providers.contacts"
    "com.google.android.syncadapters.contacts"
    "com.android.providers.calendar"
    "com.google.android.syncadapters.calendar"
    "com.android.providers.userdictionary"
    "com.google.android.backuptransport"
    "com.android.backupconfirm"
    "com.android.sharedstoragebackup"
    "com.android.wallpaperbackup"
    "com.android.settings.intelligence"

    # --- Setup & Recommendations Bloat ---
    "com.google.android.partnersetup"
    "com.google.android.onetimeinitializer"
    "com.android.onetimeinitializer"
    "com.google.android.leanbacklauncher.recommendations"
    "com.google.android.leanbacklauncher"
    "com.google.android.tvrecommendations"
)

echo "Disabling unnecessary bloatware safely via pm disable-user --user 0..."
echo ""

SUCCESS_COUNT=0
SKIP_COUNT=0

for pkg in "${TARGET_PACKAGES[@]}"; do
    res=$(./platform-tools/adb -s "${TV_IP}:${PORT}" shell pm disable-user --user 0 "$pkg" 2>/dev/null || true)
    if [[ "$res" == *"disabled-user"* ]]; then
        echo "  [DISABLED] $pkg"
        ((SUCCESS_COUNT++))
    else
        echo "  [SKIPPED / ALREADY OFF] $pkg"
        ((SKIP_COUNT++))
    fi
done

echo ""
echo "=========================================================="
echo "  ✅ Done! $SUCCESS_COUNT packages newly disabled, $SKIP_COUNT already disabled/skipped."
echo "=========================================================="
