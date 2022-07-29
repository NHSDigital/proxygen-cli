#!/bin/bash
set -e

echo "Uninstalling proxygen"
rm -rf ~/.paas
rm -f ~/.paasrc
sed -i '/.paas\/bin:$PATH/d' ~/.bashrc
sed -i '/.paas\/bin:$PATH/d' ~/.profile
echo "Proxygen is now uninstalled!"
