#!/bin/bash -e

source ./janus-version

git clone https://github.com/meetecho/janus-gateway.git
cd janus-gateway
git checkout ${JANUS_VERSION}
sudo mkdir -p /usr/include/janus
sudo cp {.,plugins}/*.h /usr/include/janus
