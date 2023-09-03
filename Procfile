nginx: make nginx_proxy
redis: make redisserver
global: PORT=$GLOBAL_PORT gunicorn -c global/configs/live/global_gunicorn.py global.configs.live.global_wsgi
website: PORT=$WEBSITE_PORT gunicorn -c website/configs/live/website_gunicorn.py website.configs.live.website_wsgi
