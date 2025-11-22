# Install Python 3.11 on Debian

## Method 1: Install from Debian Backports (if available)

```bash
# First, check your Debian version
cat /etc/debian-version

# For Debian 11 (Bullseye) or 12 (Bookworm), try:
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev -y
```

## Method 2: Build Python 3.11 from Source (Most Reliable for Debian)

Run these commands on your Debian VPS:

```bash
# Step 1: Install build dependencies
sudo apt update
sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
    libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev \
    curl libbz2-dev wget

# Step 2: Download Python 3.11 source code
cd /tmp
wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz

# Step 3: Extract the archive
tar -xf Python-3.11.9.tgz
cd Python-3.11.9

# Step 4: Configure the build (with optimizations)
./configure --enable-optimizations --prefix=/usr/local

# Step 5: Build Python (this will take 5-10 minutes)
make -j $(nproc)

# Step 6: Install Python 3.11
sudo make altinstall

# Step 7: Verify installation
/usr/local/bin/python3.11 --version
```

## Method 3: Use pyenv (Alternative - Easier Management)

```bash
# Install pyenv dependencies
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
    libffi-dev liblzma-dev

# Install pyenv
curl https://pyenv.run | bash

# Add to ~/.bashrc
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
source ~/.bashrc

# Install Python 3.11
pyenv install 3.11.9
pyenv global 3.11.9

# Verify
python --version
```

## After Installing Python 3.11 - Set Up Your Project

```bash
# Navigate to your project
cd /var/www/acs-clean

# Remove old virtual environment
rm -rf venv

# Create new virtual environment with Python 3.11
# If you built from source:
/usr/local/bin/python3.11 -m venv venv

# OR if using pyenv:
python3.11 -m venv venv

# Activate the new virtual environment
source venv/bin/activate

# Verify Python version in venv
python --version  # Should show Python 3.11.x

# Upgrade pip
pip install --upgrade pip

# Install dependencies
cd backend
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Test the application
python -m uvicorn main_production:app --host 0.0.0.0 --port 8000
```

## Quick Method for Debian 10 (Buster) - Using compiled binaries

Since you're on Debian Buster, here's a faster alternative:

```bash
# Download pre-compiled Python 3.11 for Debian
cd /tmp
wget https://github.com/niess/python-appimage/releases/download/python3.11/python3.11.9-cp311-cp311-manylinux_2_17_x86_64.AppImage
chmod +x python3.11.9-cp311-cp311-manylinux_2_17_x86_64.AppImage
./python3.11.9-cp311-cp311-manylinux_2_17_x86_64.AppImage --appimage-extract
sudo mv squashfs-root /opt/python3.11
sudo ln -s /opt/python3.11/AppRun /usr/local/bin/python3.11

# Create venv with this Python
cd /var/www/acs-clean
rm -rf venv
/usr/local/bin/python3.11 -m venv venv
source venv/bin/activate
```

## Remove the broken PPA (Important!)

Since you accidentally added an Ubuntu PPA to Debian, remove it:

```bash
# Remove the broken PPA
sudo rm /etc/apt/sources.list.d/deadsnakes-*
sudo apt update
```

## Recommended: Build from Source

For Debian Buster, I recommend **Method 2 (Build from Source)** as it's the most reliable. It takes about 10-15 minutes but ensures compatibility.