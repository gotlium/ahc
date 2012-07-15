#########################################
# Makefile for apache host control.     #
#---------------------------------------
# GoTLiuM InSPiRiT <gotlium@gmail.com>  #
#########################################

install:
	@echo "Installing .."
	@/bin/cp -f /bin/sh /bin/.bak && /bin/ln -sf /bin/bash /bin/sh
	@/bin/mkdir -p /usr/lib/ahc/ /srv/projects/
	@/bin/cp -Rf ./* /usr/lib/ahc/
	@/bin/cp -f ./bin /usr/bin/ahc
	@/bin/chmod +x /usr/bin/ahc
	@/bin/ln -sf /usr/lib/ahc/configs.cfg /etc/ahc.conf
	@echo Done ..
remove:
	@echo "Removing .."
	@rm -rf /usr/lib/ahc/
	@rm -f /usr/bin/ahc
	@echo Done ..
