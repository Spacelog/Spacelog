redis: redis-server
global: gunicorn -c global/configs/live/global_gunicorn.py global.configs.live.global_wsgi
website: gunicorn -c website/configs/live/website_gunicorn.py website.configs.live.website_wsgi
