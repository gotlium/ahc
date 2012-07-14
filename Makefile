#########################################
# Makefile for apache host control.     #
#---------------------------------------
# GoTLiuM InSPiRiT <gotlium@gmail.com>  #
#########################################

install:
	@echo "Installing .."
	@cp /bin/sh{,.bak} && ln -sf /bin/bash /bin/sh
	@/bin/mkdir -p /usr/lib/ahc/ /srv/projects/
	@cp -Rf ./* /usr/lib/ahc/
	@cp -f ./bin /usr/bin/ahc
	@chmod +x /usr/bin/ahc
	@ln -sf /usr/lib/ahc/configs.cfg /etc/ahc.conf
	@echo Done ..
remove:
	@echo "Removing .."
	@rm -rf /usr/lib/ahc/
	@rm -f /usr/bin/ahc
	@echo Done ..
