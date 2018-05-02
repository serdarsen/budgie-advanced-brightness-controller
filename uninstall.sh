#!/bin/bash

PLUGIN_DIR="/usr/lib/budgie-desktop/plugins"

ICON_DIR="/usr/share/pixmaps"

declare -a icons=("u-brightness-controller-symbolic.svg")

# Pre-install checks
if [ $(id -u) = 0 ]
then
    echo "FAIL: Please run this script as your normal user (not using sudo)."
    exit 1
fi

if [ ! -d "$PLUGIN_DIR" ]
then
    echo "FAIL: The Budgie plugin directory does not exist: $PLUGIN_DIR"
    exit 1
fi

function fail() {
    echo "FAIL: Uninstallation failed. Please note any errors above."
    exit 1
}


if [ ! -d "$ICON_DIR" ]
then
    echo "FAIL: The Icon directory does not exist: $ICON_DIR"
fi

function fail_icon() {
    echo "FAIL: Icon Uninstallation failed. Please note any errors above."
}


# Actual uninstallation
echo "Uninstalling U Brightness Controller to $PLUGIN_DIR"

sudo rm -rf "${PLUGIN_DIR}/UBrightnessController" || fail
sudo rm -rf "./cache/u-brightness-controller" || fail
sudo rm -rf "./config/u-brightness-controller" || fail

# icon uninstallation
for icon in "${icons[@]}"
do
   sudo rm -rf "${ICON_DIR}/${icon}" || fail_icon
done

budgie-panel --replace &

echo "Done. Browser Profile Launcher Uninstalled."
