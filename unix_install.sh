#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Install OpenSSL on Debian/Ubuntu-based systems
install_on_debian() {
    echo "Detected Debian-based system. Installing $1..."
    sudo apt update
    sudo apt install -y $1
}

# Install OpenSSL on Red Hat/CentOS/Fedora-based systems
install_on_redhat() {
    echo "Detected Red Hat-based system. Installing $1..."
    sudo yum install -y $1
}

# Install OpenSSL on Arch-based systems
install_on_arch() {
    echo "Detected Arch-based system. Installing $1..."
    sudo pacman -Sy --noconfirm $1
}

# Install OpenSSL on macOS
install_on_macos() {
    echo "Detected macOS. Installing $1..."
    if command_exists brew; then
        brew install $1
    else
        echo "Homebrew is not installed. Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        brew install $1
    fi
}

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
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi

if command -v ffmpeg > /dev/null 2>&1; then
    echo "ffmpeg exists."
else
    # Detect the platform and install ffmpeg accordingly
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Detect the package manager
        if command_exists apt; then
            install_on_debian "ffmpeg"
        elif command_exists yum; then
            install_on_redhat "ffmpeg"
        elif command_exists pacman; then
            install_on_arch "ffmpeg"
        else
            echo "Unsupported Linux distribution."
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        install_on_macos "ffmpeg"
    else
        echo "Unsupported operating system."
        exit 1
    fi
fi

if command -v openssl > /dev/null 2>&1 || .venv/bin/pip list | grep -q "pycryptodome"; then
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
            echo "Installing openssl."
            # Detect the platform and install OpenSSL accordingly
            if [[ "$OSTYPE" == "linux-gnu"* ]]; then
                # Detect the package manager
                if command_exists apt; then
                    install_on_debian "openssl"
                elif command_exists yum; then
                    install_on_redhat "openssl"
                elif command_exists pacman; then
                    install_on_arch "openssl"
                else
                    echo "Unsupported Linux distribution."
                    exit 1
                fi
            elif [[ "$OSTYPE" == "darwin"* ]]; then
                install_on_macos "openssl"
            else
                echo "Unsupported operating system."
                exit 1
            fi
            ;;
    esac
fi

sed -i.bak "1s|.*|#!.venv/bin/python3|" run.py
echo "Everything is installed!"
