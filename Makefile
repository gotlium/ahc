#########################################
# Makefile for apache host control.     #
#---------------------------------------
# GoTLiuM InSPiRiT <gotlium@gmail.com>  #
#########################################

install:
	@echo "Installing .."
	@/bin/cp -f /bin/sh /bin/sh.bak && /bin/ln -sf /bin/bash /bin/sh
	@/bin/mkdir -p /usr/lib/ahc/ /srv/projects/
	@/bin/cp -Rf ./* /usr/lib/ahc/
	@/bin/cp -f ./bin.sh /usr/bin/ahc
	@/bin/chmod +x /usr/bin/ahc
	@/bin/ln -sf /usr/lib/ahc/configs.cfg /etc/ahc.conf
	@echo "Done."
remove:
	@echo "Removing .."
	@/bin/rm -rf /usr/lib/ahc/
	@/bin/rm -f /usr/bin/ahc
	@/bin/rm -f /etc/ahc.conf
	@/bin/ln -sf /bin/dash /bin/sh
	@echo "Done."
