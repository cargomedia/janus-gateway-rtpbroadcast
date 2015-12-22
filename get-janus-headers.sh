#!/bin/bash -e

source ./janus-version

git clone https://github.com/meetecho/janus-gateway.git
cd janus-gateway
git checkout ${JANUS_VERSION}
mkdir -p /usr/include/janus
cp {.,plugins}/*.h /usr/include/janus
