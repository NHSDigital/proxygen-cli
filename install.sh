#!/bin/bash
set -e

which python || echo "Python not found. Please install Python >= 3.8"
git clone git@github.com:NHSDigital/paas-client.git ~/.paas

# just adding a newline between existing content
echo '' >> ~/.bashrc
echo '' >> ~/.bashrc
echo '' >> ~/.profile
echo '' >> ~/.profile

echo 'export PATH="${HOME}/.paas/bin:$PATH"' >> ~/.profile
echo 'export PATH="${HOME}/.paas/bin:$PATH"' >> ~/.bashrc

. ${HOME}/.profile
. ${HOME}/.bashrc

python3 -m venv ${HOME}/.paas/env && . ${HOME}/.paas/env/bin/activate && pip install -r requirements.txt

sed -i "1s%.*%#\!${HOME}/.paas/env/bin/python%" ${HOME}/.paas/paas-entry.py

base64 -d <<<X19fX19fX19fXyAgX19fX18gICAgICBfX19fXyAgICBfX19fX19fX18KXF9fX19\fXyAgIFwvICBfICBcICAgIC8gIF8gIFwgIC8gICBfX19fXy8KIHwgICAgIF9fXy8gIC9fXCAgXCAgLyAgL19cICBcIFxfX19fXyAgXCAKIHwgICAgfCAgLyAgICB8ICAgIFwvICAgIHwgICAgXC8gICAgICAgIFwKIHxfX19ffCAgXF9fX198X18gIC9cX19fX3xfXyAgL19fX19fX18gIC8KICAgICAgICAgICAgICAgICBcLyAgICAgICAgIFwvICAgICAgICBcLyA= && echo -e "\e[32m...is now installed!\e[0m"
echo ""
echo -e "\e[36m- Get in contact with APIM and get your credentials...\e[0m"
echo -e "\e[35m- Follow us at: https://github.com/NHSDigital\e[0m"