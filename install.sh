#!/usr/bin/env bash

set -o pipefail

# Check if user is root
if [[ $(id -u) -ne 0 ]] ; then echo "Please run as superuser." ; exit 1 ; fi


echo "Update repository..."
apt-get update -y


echo "Install Python..."
apt-get -y install python3 python3-pip python3-venv python3-dev


echo "Create Python virtual environment..."
# create environment as non root
sudo -u $SUDO_USER python3 -m venv venv

source venv/bin/activate

echo "Install python packages..."
python3 -m pip install --default-timeout=100 -r requirements.txt

deactivate

chmod +x run.sh

mkdir -p cookies

chmod 777 cookies

echo "Installation completed."
