indexer                   = backend/indexer.py
website_screen_css        = website/static/css/screen.css
website_source_screen_css = website/static/css/screen/*.css
global_screen_css         = global/static/css/screen.css
global_source_screen_css  = global/static/css/screen/*.css
webserver_ip             ?= 0.0.0.0
webserver_port           ?= 8000
global_port              ?= 8001

all: reindex productioncss

reindex: $(indexer)
	rm -rf xappydb
	python -m backend.indexer
	python -m backend.stats_porn

productioncss:	$(website_screen_css) $(global_screen_css)

$(website_screen_css): $(website_source_screen_css)
	cssprepare --optimise --extended-syntax \
		$(website_source_screen_css) > $(website_screen_css)

$(global_screen_css): $(global_source_screen_css)
	cssprepare --optimise --extended-syntax \
		$(global_source_screen_css) > $(global_screen_css)

devserver:
	python -m website.manage runserver $(webserver_ip):$(webserver_port)

devcss:
	cssprepare --optimise --extended-syntax \
		--pipe $(website_screen_css) $(website_source_screen_css)

devserver_global:
	python -m global.manage runserver $(webserver_ip):$(global_port)

devcss_global:
	cssprepare --optimise --extended-syntax \
		--pipe $(global_screen_css) $(global_source_screen_css)

thumbnails:
	cd website/static/img/missions/a13/; python resize.py
