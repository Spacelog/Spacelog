indexer                   = backend/indexer.py
website_scss_sources      = $(wildcard website/static/css/*.scss)
website_css_targets       = $(patsubst %.scss,%.css,$(website_scss_sources))
website_scss_components   = $(wildcard website/static/css/*/*.scss)
global_scss_sources       = $(wildcard global/static/css/*.scss)
global_css_targets        = $(patsubst %.scss,%.css,$(global_scss_sources))
global_scss_components    = $(wildcard global/static/css/*/*.scss)
PYTHON                   ?= python
SASS                     ?= pyscss

# Dev Django runserver variables
dev_webserver_ip         ?= 0.0.0.0
WEBSITE_PORT             ?= 8001
GLOBAL_PORT              ?= 8000
NGINX_PORT               ?= 9000
PROJECT_DOMAIN           ?= dev.spacelog.org

all: reindex collectstatic

dirty: copyxapian productioncss copy_statsporn

collectstatic: productioncss statsporn
	DJANGOENV=live $(PYTHON) -m website.manage collectstatic --noinput --ignore=*.scss
	DJANGOENV=live $(PYTHON) -m global.manage collectstatic --noinput --ignore=*.scss

reindex: $(indexer)
	rm -rf xappydb
	$(PYTHON) -m backend.indexer

# backwards compatibility
build_statsporn: statsporn

statsporn:
	$(PYTHON) -m backend.stats_porn

copy_statsporn:
	$(foreach d, $(wildcard ../current/missions/*/images/stats), cp -a $d `echo $d | sed 's#../current/##'`;)

productioncss:	$(website_css_targets) $(global_css_targets)

# only use this in production, it'll explode entertainingly otherwhere
copyxapian:
	cp -a ../current/xappydb xappydb

$(website_css_targets): $(website_scss_sources) $(website_scss_components)
	$(SASS) -t compressed $(@:.css=.scss) > $@

$(global_css_targets): $(global_scss_sources) $(global_scss_components)
	$(SASS) -t compressed $(@:.css=.scss) > $@

devserver:
	$(PYTHON) -m website.manage runserver $(dev_webserver_ip):$(WEBSITE_PORT)

devcss:
	watch -n 0.1 make $(website_css_targets)

devserver_global:
	$(PYTHON) -m global.manage runserver $(dev_webserver_ip):$(GLOBAL_PORT)

devcss_global:
	watch -n 0.1 make $(global_css_targets)

thumbnails:
	cd website/static/img/missions/a13/; $(PYTHON) resize.py

# assume there's no artemis screen session already, and just make one from scratch
screen:
	screen -dmS artemis
	sleep 1
	screen -r artemis -X source screenstart
	screen -r artemis

# it's all the rage to avoid shell scripts, apparently
gunicornucopia: gunicorn_global gunicorn_website

gunicornicide:
	-start-stop-daemon --pidfile ~/gunicorn-global.pid --remove-pidfile -K
	-start-stop-daemon --pidfile ~/gunicorn-website.pid --remove-pidfile -K

gunicorn_global:
	ENV/bin/gunicorn -c global/configs/live/global_gunicorn.py --daemon --pid ~/gunicorn-global.pid --error-logfile ~/gunicorn-global.log global.configs.live.global_wsgi

gunicorn_website:
	ENV/bin/gunicorn -c website/configs/live/website_gunicorn.py --daemon --pid ~/gunicorn-website.pid --error-logfile ~/gunicorn-website.log website.configs.live.website_wsgi

nginx_proxy:
	sed \
	  -e 's|$${NGINX_PORT}|'"${NGINX_PORT}"'|g' \
	  -e 's|$${GLOBAL_PORT}|'"${GLOBAL_PORT}"'|g' \
	  -e 's|$${WEBSITE_PORT}|'"${WEBSITE_PORT}"'|g' \
	  -e 's|$${PROJECT_DOMAIN}|'"${PROJECT_DOMAIN}"'|g' \
	  nginx_proxy.conf.template \
	> /etc/nginx/sites-available/default
	exec nginx -g 'daemon off;'

redisserver:
	# Enable swap memory if we're in an environment that supports it,
	# because in low-/fixed-memory environments, Redis quickly gets OOM-killed
	if ! grep '\/proc\/sys\b.*\bro\b' /proc/mounts > /dev/null; then \
	  fallocate -l 512M /swapfile; \
	  chmod 0600 /swapfile; \
	  mkswap /swapfile; \
	  echo 10 > /proc/sys/vm/swappiness; \
	  swapon /swapfile; \
	  echo 1 > /proc/sys/vm/overcommit_memory; \
	fi
	# Actually run Redis
	redis-server /etc/redis/redis.conf --logfile "" --daemonize no
