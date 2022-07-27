#!/bin/bash
set -e

git clone git@github.com:NHSDigital/paas-client.git ~/.paas

# just adding a newline between existing content
echo '' >> ~/.bashrc
echo '' >> ~/.bashrc
echo '' >> ~/.profile
echo '' >> ~/.profile

echo 'export PATH="${HOME}/.paas/bin:$PATH"' >> ~/.profile
. ${HOME}/.profile

python3 -m venv ${HOME}/.paas/env && . ${HOME}/.paas/env/bin/activate && pip install -r requirements.txt

sed -i "1s%.*%#\!${HOME}/.paas/env/bin/python%" ${HOME}/.paas/paas-entry.py


