#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Install on Debian/Ubuntu-based systems
install_on_debian() {
    echo "Installing $1..."
    sudo apt update
    sudo apt install -y $1
}

# Install on Red Hat/CentOS/Fedora-based systems
install_on_redhat() {
    echo "Installing $1..."
    sudo yum install -y $1
}

# Install on Arch-based systems
install_on_arch() {
    echo "Installing $1..."
    sudo pacman -Sy --noconfirm $1
}

# Install on BSD-based systems
install_on_bsd() {
    echo "Installing $1..."
    env ASSUME_ALWAYS_YES=yes pkg install -y $1
}

# Install on macOS
install_on_macos() {
    echo "Installing $1..."
    if command_exists brew; then
        brew install $1
    else
        echo "Homebrew is not installed. Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        brew install $1
    fi
}

set -e

# Check and install Python3
# if command_exists python3 > /dev/null 2>&1; then
#     echo "Checking Python..."
# else
#     # Detect the platform and install Python3 accordingly
#     if [[ "$OSTYPE" == "linux-gnu"* ]]; then
#         # Detect the package manager
#         if command_exists apt; then
#             install_on_debian "python3"
#         elif command_exists yum; then
#             install_on_redhat "python3"
#         elif command_exists pacman; then
#             install_on_arch "python-pip"
#         else
#             echo "Unsupported Linux distribution."
#             exit 1
#         fi
#     elif [[ "$OSTYPE" == "bsd"* ]]; then
#         echo "Detected BSD-based system."
#         install_on_bsd "python39"
#     elif [[ "$OSTYPE" == "darwin"* ]]; then
#         install_on_macos "python"
#     else
#         echo "Unsupported operating system."
#         exit 1
#     fi
# fi

# Get the Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')

# Compare the Python version with 3.8
REQUIRED_VERSION="3.8"

if [[ $(echo -e "$PYTHON_VERSION\n$REQUIRED_VERSION" | sort -V | head -n1) == "$REQUIRED_VERSION" ]]; then
    echo "Python version $PYTHON_VERSION is >= $REQUIRED_VERSION. Continuing..."
else
    echo "ERROR: Python version $PYTHON_VERSION is < $REQUIRED_VERSION. Exiting..."
    exit 1
fi

if [ -d ".venv/" ]; then
    echo ".venv exists."
else
    echo "Making .venv and installing requirements.txt."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
       # Detect the package manager
       if command_exists apt; then
           echo "Detected Debian-based system. Checking python3-venv."
           if dpkg -l | grep -q "python3-venv"; then
                echo "python3-venv found."
           else
               echo "python3-venv not found, installing..."
               install_on_debian "python3-venv"
           fi
       fi
    fi
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt

fi

if command_exists ffmpeg > /dev/null 2>&1; then
    echo "ffmpeg exists."
else
    echo "ffmpeg does no exists."
    # Detect the platform and install ffmpeg accordingly
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Detect the package manager
        if command_exists apt; then
            echo "Detected Debian-based system."
            install_on_debian "ffmpeg"
        elif command_exists yum; then
            echo "Detected Red Hat-based system."
            echo "Installing needed repos for ffmpeg..."
            echo "Enabling crb..."
            sudo yum config-manager --set-enabled crb > /dev/null 2>&1
            echo "crb enabled."
            echo "Installig epel..."
            sudo yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-$(rpm -E %rhel).noarch.rpm https://dl.fedoraproject.org/pub/epel/epel-next-release-latest-$(rpm -E %rhel).noarch.rpm > /dev/null 2>&1
            echo "epel installed."
            echo "Adding ffmpeg repos..."
            sudo yum install -y --nogpgcheck https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-$(rpm -E %rhel).noarch.rpm https://mirrors.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-$(rpm -E %rhel).noarch.rpm > /dev/null 2>&1
            echo "ffmpeg repos added."
            install_on_redhat "ffmpeg"
        elif command_exists pacman; then
            echo "Detected Arch-based system."
            install_on_arch "ffmpeg"
        else
            echo "Unsupported Linux distribution."
            exit 1
        fi
    elif [[ "$OSTYPE" == "bsd"* ]]; then
        echo "Detected BSD-based system."
        install_on_bsd "ffmpeg"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Detected macOS."
        install_on_macos "ffmpeg"
    else
        echo "Unsupported operating system."
        exit 1
    fi
fi

if command_exists openssl > /dev/null 2>&1 || .venv/bin/pip list | grep -q "pycryptodome"; then
    echo "openssl or pycryptodome exists."
else
    echo "Please choose an option:"
    echo "1) openssl"
    echo "2) pycryptodome"
    read -p "Enter your choice (1): " choice
    case $choice in
        2)
            echo "Installing pycryptodome."
            .venv/bin/pip install pycryptodome
            ;;
        *)
            # Detect the platform and install OpenSSL accordingly
            if [[ "$OSTYPE" == "linux-gnu"* ]]; then
                # Detect the package manager
                if command_exists apt; then
                    echo "Detected Debian-based system."
                    install_on_debian "openssl"
                elif command_exists yum; then
                    echo "Detected Red Hat-based system."
                    install_on_redhat "openssl"
                elif command_exists pacman; then
                    echo "Detected Arch-based system."
                    install_on_arch "openssl"
                else
                    echo "Unsupported Linux distribution."
                    exit 1
                fi
            elif [[ "$OSTYPE" == "bsd"* ]]; then
                echo "Detected BSD-based system."
                install_on_bsd "openssl"
            elif [[ "$OSTYPE" == "darwin"* ]]; then
                echo "Detected macOS."
                install_on_macos "openssl"
            else
                echo "Unsupported operating system."
                exit 1
            fi
            ;;
    esac
fi

sed -i.bak "1s|.*|#!.venv/bin/python3|" run.py
sudo chmod +x run.py
echo "Everything is installed!"
echo "Run StreamingCommunity with './run.py'"
