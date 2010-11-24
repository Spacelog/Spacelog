screen_css        = css/screen.css
source_screen_css = css/screen/*.css


productioncss:	$(screen_css)

$(screen_css):
	cssprepare --optimise --extended-syntax \
		$(source_screen_css) > $(screen_css)

devcss:
	cssprepare --optimise --extended-syntax \
		--pipe $(screen_css) $(source_screen_css)
