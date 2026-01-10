# Function to detect OS (called once at shell startup)
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case "$ID" in
            ubuntu|debian)
                echo "ubuntu"
                ;;
            rhel|centos|rocky|almalinux|fedora)
                echo "redhat"
                ;;
            *)
                echo "linux"
                ;;
        esac
    elif [ -f /etc/redhat-release ]; then
        echo "redhat"
    else
        echo "linux"
    fi
}

# Set OS variable once
OS_TYPE=$(detect_os)

# Best practice colors for prompt:
# - OS: Magenta/Purple (51/135) - distinctive identifier
# - Date: Orange (208) - temporal info, muted
# - Username: Green (46/82) - standard, safe
# - Hostname: Cyan (51/87) - system identifier
# - Directory: Blue (33/39) - navigational info
# - Separator (@): Yellow (226/220) - visual separator

export PS1="\[$(tput setaf 135)\][$OS_TYPE]  \[$(tput setaf 208)\]\d  \[$(tput setaf 82)\]\u\[$(tput setaf 226)\]@\[$(tput setaf 87)\]\h \[$(tput setaf 39)\]\w 
\[$(tput sgr0)\]$ "
