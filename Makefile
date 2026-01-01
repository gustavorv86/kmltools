SHELL:=/bin/bash

PYSRC:=$(wildcard *.py)

all:

install: $(PYSRC)
	if [ ! -f /usr/lib/python3/dist-packages/xmltodict.py ]; then sudo apt -y install python3-xmltodict; fi
	mkdir -p "${HOME}/.local/bin"
	chmod u+x $(PYSRC)
	cp $(PYSRC) "${HOME}/.local/bin"
	@echo "Install done."
