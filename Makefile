indexer           = backend/indexer.py
screen_css        = website/static/css/screen.css
source_screen_css = website/static/css/screen/*.css

all: reindex productioncss

reindex: $(indexer)
	rm -rf xappydb
	python -m backend.indexer

productioncss:	$(screen_css)

$(screen_css):
	cssprepare --optimise --extended-syntax \
		$(source_screen_css) > $(screen_css)

devcss:
	cssprepare --optimise --extended-syntax \
		--pipe $(screen_css) $(source_screen_css)
