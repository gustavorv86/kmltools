
PYSRC := $(wildcard *.py)

all:

install: $(PYSRC)
	mkdir -p "${HOME}/.local/bin"
	chmod u+x $(PYSRC)
	cp $(PYSRC) "${HOME}/.local/bin"

