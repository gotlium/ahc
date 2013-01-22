#########################################
# Makefile for apache host control.     #
#---------------------------------------
# GoTLiuM InSPiRiT <gotlium@gmail.com>  #
#########################################

DESTDIR=
BINDIR=$(DESTDIR)/usr/bin/
ETCDIR=$(DESTDIR)/etc

install:
	@echo "Installing .."
	@if [ ! -d $(BINDIR) ]; then mkdir -p $(BINDIR); fi
	@if [ ! -d $(ETCDIR) ]; then mkdir -p $(ETCDIR); fi
	@/bin/cp -f /bin/sh /bin/sh.bak && /bin/ln -sf /bin/bash /bin/sh
	@/bin/mkdir -p $(DESTDIR)/usr/lib/ahc/ $(DESTDIR)/srv/projects/
	@/bin/cp -Rf ./* $(DESTDIR)/usr/lib/ahc/
	@/bin/cp -f ./bin.sh $(BINDIR)ahc
	@/bin/chmod +x $(BINDIR)ahc
	@/bin/chmod +x /usr/lib/ahc/templates/git-jail.sh
	@/bin/ln -sf $(DESTDIR)/usr/lib/ahc/configs.cfg $(DESTDIR)/etc/ahc.conf
	@echo "Done."
remove:
	@echo "Removing .."
	@/bin/rm -rf $(DESTDIR)/usr/lib/ahc/
	@/bin/rm -f $(BINDIR)/ahc
	@/bin/rm -f $(DESTDIR)/etc/ahc.conf
	@/bin/ln -sf /bin/dash /bin/sh
	@echo "Done."
