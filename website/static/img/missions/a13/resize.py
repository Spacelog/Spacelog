from PIL import Image
import os

crop_width = 600
crop_height = 100

for filename in os.listdir("."):
    if filename.endswith(".jpg") and not filename.endswith("-thumb.jpg"):
        basename = filename[:-4]
        thumbname = "%s-thumb.jpg" % basename
        if os.path.exists(thumbname):
            #pass
            continue
        print "Converting %s" % filename
        # Step one: thumbnail
        source = Image.open(filename)
        thumbnail = source.copy()
        thumbnail.thumbnail((1024, 1024))
        thumbnail.save(filename)
        # Step two: slice
        slice = source.copy()
        slice.thumbnail((crop_width, 40000))
        w, h = slice.size
        mid = (h // 2)
        start = mid - (crop_height // 2)
        slice = slice.crop((0, start, crop_width, start + crop_height))
        slice.save(thumbname)

