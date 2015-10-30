Vagrant.configure('2') do |config|
  config.vm.box = 'cargomedia/debian-7-amd64-default'

  config.vm.provision 'deps', type: 'shell', inline: [
     'cd /vagrant',
     'sudo apt-get update',
     'apt-get -y install libmicrohttpd-dev libjansson-dev libnice-dev \
     libssl-dev libsrtp-dev libsofia-sip-ua-dev libglib2.0-dev \
     libopus-dev libogg-dev libini-config-dev libcollection-dev \
     libavutil-dev libavcodec-dev libavformat-dev \
     pkg-config gengetopt libcurl4-openssl-dev libtool automake cmake',
     'cd',
     # Dep 1
     'wget https://github.com/cisco/libsrtp/archive/v1.5.0.tar.gz',
     'tar xfv v1.5.0.tar.gz',
     'cd libsrtp-1.5.0',
     './configure --prefix=/usr --enable-openssl --libdir=/usr/lib64',
     'make libsrtp.so && make uninstall && make install',
     'cd -',
     # Dep 2
     'rm -fr usrsctp',
     'git clone https://github.com/sctplab/usrsctp',
     'cd usrsctp',
     './bootstrap',
     './configure --prefix=/usr && make && make uninstall && make install',
     'cd -',
     # Dep 3
     'rm -fr libwebsockets',
     'git clone git://git.libwebsockets.org/libwebsockets',
     'cd libwebsockets',
     'mkdir build',
     'cd build',
     'cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr ..',
     'make && make install',
     'cd -',
  ].join(' && ')

  config.vm.provision 'janus', type: 'shell', inline: [
    'cd /vagrant/janus-gateway',
    './configure --prefix=/home/vagrant/janus --disable-docs --disable-rabbitmq --enable-post-processing',
    'make && make install'
  ].join(' && ')
end
