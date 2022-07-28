#!/bin/bash
set -e

rm -rf ~/.paas
rm -f ~/paasrc
sed -i '/.paas\/bin:$PATH/d' ~/.bashrc
sed -i '/.paas\/bin:$PATH/d' ~/.profile
