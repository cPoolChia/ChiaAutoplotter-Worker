# ChiaAutoplotter-Worker Installation

## 1. Install python3.9 and pip
```shell
# Go to root directory
cd

sudo apt-get update
sudo apt-get upgrade -y

sudo add-apt-repository ppa:deadsnakes/ppa
# Make sure to press enter when prompted
sudo apt install python3.9
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py 
python3.9 get-pip.py

# If you see any permissions errors, you may need to use
python3.9 get-pip.py –user
# If you get an error like No module named 'distutils.util' when you 
# run python3.9 get-pip.py, and you are on a Debian-based Linux 
# distribution, run
sudo apt install python3.9-distutils
# and then rerun your get-pip.py command. If you are not on a 
# Debian-based distribution, use the equivalent command for your 
# distribution's package manager.
python3.9 get-pip.py
```
<i>Detailed:</i>
* <i>[python3.9](https://linuxize.com/post/how-to-install-python-3-9-on-ubuntu-20-04/)</i>
* <i>[pip](https://stackoverflow.com/questions/65644782/how-to-install-pip-for-python-3-9-on-ubuntu-20-04)</i>

## 2. Install Chia
<i>It needs to be located at</i> `/root/chia-blockchain`<i>, just git clone while in</i> `/root/`
```shell
# Go to root directory
cd

# Install Git
sudo apt install git -y

# Checkout the source and install
git clone https://github.com/Chia-Network/chia-blockchain.git -b latest --recurse-submodules
cd chia-blockchain

sh install.sh
. ./activate
chia init
```
<i>Detailed [here](https://github.com/Chia-Network/chia-blockchain/wiki/INSTALL).</i>

## 3. Download ChiaAutoplotter-Worker 
<i>It needs to be located at</i> `/root/ChiaAutoplotter-Worker`<i>, just git clone while in</i> `/root/`
```shell
# Go to root directory
cd

# Checkout the source and install
git clone https://github.com/cPoolChia/ChiaAutoplotter-Worker.git -b main --recurse-submodules
```

## 4. Install poetry
```shell
python3.9 -m pip install poetry
```
<i>Detailed [here](https://python-poetry.org/).</i>


## 5. Use screen command to run a screen and start a server, that will not close on ssh disconnect
```shell
# Go to root directory
cd

# Check if screen command is installed
screen –version

# If not install it using:
sudo apt install screen

screen
```
<i>Detailed [here](https://linuxize.com/post/how-to-use-linux-screen/).</i>

## 6. In screen, go to ChiaAutoplotter-Worker directory and run worker
```shell
cd /ChiaAutoplotter-Worker
python3.9 -m poetry install
python3.9 -m poetry run uvicorn app:app --reload --host 0.0.0.0
```
Close a new screen (with shell) – `Ctrl+a` and `Ctrl+d`

## 7. Open port 8000 on server (if needed (if it’s in local network), redirect to it in router)
```shell
sudo ufw allow 8000
```
<i>Detailed [here](https://linuxize.com/post/how-to-setup-a-firewall-with-ufw-on-ubuntu-20-04/).</i>

## 8. Add server data to ChiaAutoPlotter web app
`Server` > `Add server`, then fill in data and push the add button.
