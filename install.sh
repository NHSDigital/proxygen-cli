#!/bin/bash
set -e

[ -d ${HOME}/.paas ] && { echo "proxygen is already installed\n If you want to reinstall please first uninstall with ${HOME}/.paas/uninstall.sh"; exit 1; }
python3 -c "import sys; assert sys.version_info >= (3,8)" || { echo "Python not found. Please install Python >= 3.8"; exit 1; }
git clone https://github.com/NHSDigital/proxygen-cli.git ${HOME}/.paas

# just adding a newline between existing content
echo '' >> ~/.bashrc
echo '' >> ~/.profile

echo 'export PATH="${HOME}/.paas/bin:$PATH"' >> ~/.profile
echo 'export PATH="${HOME}/.paas/bin:$PATH"' >> ~/.bashrc

. ${HOME}/.profile
. ${HOME}/.bashrc

python3 -m venv ${HOME}/.paas/env && . ${HOME}/.paas/env/bin/activate && pip install -r ${HOME}/.paas/requirements.txt

sed -i "1s%.*%#\!${HOME}/.paas/env/bin/python%" ${HOME}/.paas/paas-entry.py

base64 -d <<<X19fX19fX19fXyAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgX19fXyAgICAgICAgICAgICAgICAgICAKXF9fX19fXyAgIFxfX19fX19fICAgX19fXyBfX18gIF9fXyBfX18uX18uICAvIF9fX1wgICBfX19fICAgIF9fX18gICAKIHwgICAgIF9fXy9cXyAgX18gXCAvICBfIFxcICBcLyAgLzwgICB8ICB8IC8gL18vICA+Xy8gX18gXCAgLyAgICBcICAKIHwgICAgfCAgICAgfCAgfCBcLyggIDxfPiApPiAgICA8ICBcX19fICB8IFxfX18gIC8gXCAgX19fLyB8ICAgfCAgXCAKIHxfX19ffCAgICAgfF9ffCAgICBcX19fXy8vX18vXF8gXCAvIF9fX198L19fX19fLyAgIFxfX18gID58X19ffCAgLyAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBcLyBcLyAgICAgICAgICAgICAgICAgICBcLyAgICAgIFwvICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA= && echo -e "\e[32m...is now installed!\e[0m"
echo ""
echo -e "\e[36m- Get in contact with APIM and get your credentials...\e[0m"
echo -e "\e[35m- Follow us at: https://github.com/NHSDigital\e[0m"
