#!/bin/bash
set -e

rm -rf ~/.paas
sed -i '/.paas\/bin:$PATH/d' ~/.bashrc
sed -i '/.paas\/bin:$PATH/d' ~/.profile
