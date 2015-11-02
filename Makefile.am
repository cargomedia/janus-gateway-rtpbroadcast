ACLOCAL_AMFLAGS = -I m4
CFLAGS = $(shell pkg-config --cflags glib-2.0) -Ijanus-gateway
CXXFLAGS = $(CFLAGS)
lib_LTLIBRARIES = libjanus_rtpbroadcast.la
libjanus_rtpbroadcast_la_SOURCES = libjanus_rtpbroadcast.c
libjanus_rtpbroadcast_la_LDFLAGS = -version-info 0:0:0 $(shell pkg-config --libs glib-2.0)

LIBS = $(shell pkg-config --libs glib-2.0)

confdir = $(exec_prefix)/etc/janus
libdir = $(exec_prefix)/lib/janus/plugins
conf_DATA = conf/janus.plugin.cm.rtpbroadcast.cfg.sample

##
# Configuration
##

config:
	$(MKDIR_P) $(DESTDIR)$(confdir)
	$(foreach config,$(conf_DATA),cp "$(CURDIR)/$(config)" "$(DESTDIR)$(confdir)/$(notdir $(basename $(config) .sample))";)
