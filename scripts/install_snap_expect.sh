spawn bash esa-snap_sentinel_linux-10.0.0.sh -c

# Define the patterns to look for and the commands to send
expect {
    "This will install ESA SNAP on your computer." {
        send "\r"
        exp_continue
    }

    "Shall the installer try to remove these directories?" {
        send "1\r"
        exp_continue
    }

    "A previous installation has been detected. Do you wish to update that installation?" {
        send "1\r"
        exp_continue
    }

    "Where should ESA SNAP be installed?" {
        send "/root/esa-snap\r"
        exp_continue
    }

    "Please enter a comma-separated list of the selected values" {
        send "\r"
        exp_continue
    }

    "Create symlinks?" {
        send "y\r"
        exp_continue
    }

    "Select the folder where you would like ESA SNAP to create symlinks, then click Next." {
        send "\r"
        exp_continue
    }

    "Configure SNAP for use with Python?" {
        send "\r"
        exp_continue
    }

    "Run SNAP Desktop?" {
        send "n\r"
        exp_continue
    }

    eof
}