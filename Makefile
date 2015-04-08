indexer                   = backend/indexer.py
website_screen_css        = website/static/css/screen.css
website_screen_sass       = website/static/css/screen.scss
website_screen_sass_components = website/static/css/screen/*.scss
global_screen_css         = global/static/css/screen.css
global_screen_sass        = global/static/css/screen.scss
global_screen_sass_components = global/static/css/*.scss
PYTHON                   ?= ./ENV/bin/python

# Dev Django runserver variables
dev_webserver_ip         ?= 0.0.0.0
dev_webserver_port       ?= 8000
dev_global_port          ?= 8001

all: reindex productioncss statsporn

dirty: copyxapian productioncss copy_statsporn

reindex: $(indexer)
	rm -rf xappydb
	$(PYTHON) -m backend.indexer

# backwards compatibility
build_statsporn: statsporn

statsporn:
	$(PYTHON) -m backend.stats_porn

copy_statsporn:
	$(foreach d, $(wildcard ../current/missions/*/images/stats), cp -a $d `echo $d | sed 's#../current/##'`;)

productioncss:	$(website_screen_css) $(global_screen_css)

# only use this in production, it'll explode entertainingly otherwhere
copyxapian:
	cp -a ../current/xappydb xappydb

$(website_screen_css): $(website_screen_sass) $(website_screen_sass_components)
	sass --style compressed \
		$(website_screen_sass) > $(website_screen_css)

$(global_screen_css): $(global_screen_sass) $(global_screen_sass_components)
	sass --style compressed \
		$(global_screen_sass) > $(global_screen_css)

devserver:
	$(PYTHON) -m website.manage runconcurrentserver $(dev_webserver_ip):$(dev_webserver_port)

devcss:
	sass --style compressed --watch $(website_screen_sass):$(website_screen_css)

devserver_global:
	$(PYTHON) -m global.manage runserver $(dev_webserver_ip):$(dev_global_port)

devcss_global:
	sass --style compressed --watch $(global_screen_sass):$(global_screen_css)

thumbnails:
	cd website/static/img/missions/a13/; $(PYTHON) resize.py

# assume there's no artemis screen session already, and just make one from scratch
screen:
	screen -dmS artemis
	sleep 1
	screen -r artemis -X source screenstart
	screen -r artemis
