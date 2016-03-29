#!/bin/bash -e

source ./janus-version

git clone https://github.com/meetecho/janus-gateway.git
cd janus-gateway
git checkout ${JANUS_VERSION}
sh autogen.sh
./configure --prefix=/usr --disable-rabbitmq --disable-docs --enable-post-processing
make
sudo make install
