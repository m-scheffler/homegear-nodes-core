AUTOMAKE_OPTIONS = subdir-objects

AM_CPPFLAGS = -Wall -std=c++11 -DFORTIFY_SOURCE=2 -DGCRYPT_NO_DEPRECATED
AM_LDFLAGS = -Wl,-rpath=/lib/homegear -Wl,-rpath=/usr/lib/homegear -Wl,-rpath=/usr/local/lib/homegear
LIBS += -Wl,-Bdynamic -lhomegear-node

libdir = $(localstatedir)/lib/homegear/node-blue/nodes/pulsecounter
lib_LTLIBRARIES = pulsecounter.la
pulsecounter_la_SOURCES = Factory.cpp MyNode.cpp
pulsecounter_la_LDFLAGS =-module -avoid-version -shared
pulsecounter_ladir = $(libdir)
pulsecounter_la_DATA = pulsecounter.hni
locale_en_usdir = $(libdir)/locales/en-US
locale_en_us_DATA = locales/en-US/pulsecounter
locale_de_dedir = $(libdir)/locales/de-DE
locale_de_de_DATA = locales/de-DE/pulsecounter
install-exec-hook:
	rm -f $(DESTDIR)$(libdir)/pulsecounter.la
