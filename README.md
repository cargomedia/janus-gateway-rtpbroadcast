# janus-gateway-cm
[janus-gateway](https://github.com/meetecho/janus-gateway) plugin for [cm-janus](https://github.com/cargomedia/cm-janus)

## Building
[![Build Status](https://travis-ci.org/cargomedia/janus-gateway-rtpbroadcast.svg)](https://travis-ci.org/cargomedia/janus-gateway-rtpbroadcast)

If you got janus-gateway-rtpbroadcast from the git repository, you will first need to run the included `autogen.sh` script
to generate the `configure` script.

```
./autogen.sh
./configure  --prefix=/opt/janus
make
make install
```
