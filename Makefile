STATIC=/usr/share
VAR=/var
PROJECT=id-verification
VERSION := $(shell head -n 1 debian/changelog | cut -d\( -f2 | cut -d\) -f1 | cut -d\~ -f1)

all:
	echo "Nothing to prepare"

${STATIC}/${PROJECT}/venv:
	mkdir -p ${STATIC}/${PROJECT}/venv
	python3 -m venv ${STATIC}/${PROJECT}/venv
	. ${STATIC}/${PROJECT}/venv/bin/activate ; pip3 install -r requirements.txt
	mkdir -p $(DESTDIR)/${STATIC}/${PROJECT}

install: ${STATIC}/${PROJECT}/venv
	mv ${STATIC}/${PROJECT}/venv $(DESTDIR)/${STATIC}/${PROJECT}
	mkdir -p $(DESTDIR)/${STATIC}/${PROJECT}
	cp -a frontend lib logs wsgi.py app.py $(DESTDIR)/${STATIC}/${PROJECT}
	mkdir -p $(DESTDIR)/etc/${PROJECT}
	cp .env-dist $(DESTDIR)/etc/${PROJECT}/${PROJECT}.conf
	cp frontend/resources/js/key.js-dist $(DESTDIR)/etc/${PROJECT}/key.js
	ln -sf /etc/${PROJECT}/key.js $(DESTDIR)/${STATIC}/${PROJECT}/frontend/resources/js/key.js
	mkdir -p $(DESTDIR)/${VAR}/${PROJECT}
