#!/bin/bash

# URL of the installer
URL="https://download.esa.int/step/snap/10_0/installers/esa-snap_sentinel_linux-10.0.0.sh"

# Download the installer
wget $URL -O esa-snap_sentinel_linux-10.0.0.sh -P /root/ALINEA/scripts/

# # Make the installer executable
chmod +x ./esa-snap_sentinel_linux-10.0.0.sh

# # Use expect to automate the installation process
/usr/bin/expect /root/ALINEA/scripts/install_snap_expect.sh
