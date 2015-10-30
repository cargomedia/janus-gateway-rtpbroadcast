ACLOCAL_AMFLAGS = -I m4
CFLAGS = $(shell pkg-config --cflags glib-2.0) -Ijanus-gateway
CXXFLAGS = $(CFLAGS)
lib_LTLIBRARIES = libjanus_streaming_cm.la
libjanus_cm_la_SOURCES = libjanus_streaming_cm.c
libjanus_cm_la_LDFLAGS = -version-info 0:0:1 $(shell pkg-config --libs glib-2.0)

LIBS = $(shell pkg-config --libs glib-2.0)

confdir = $(exec_prefix)/etc/janus
libdir = $(exec_prefix)/lib/janus/plugins
conf_DATA = conf/janus.plugin.cm.video.cfg.sample

##
# Configuration
##

config:
	$(MKDIR_P) $(DESTDIR)$(confdir)
	$(foreach config,$(conf_DATA),cp "$(CURDIR)/$(config)" "$(DESTDIR)$(confdir)/$(notdir $(basename $(config) .sample))";)
