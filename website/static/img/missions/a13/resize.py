from PIL import Image
import os

crop_width = 600
crop_height = 100

sizes = [
    (0.5, 220),
    (1, 380),
    (999, 540),
]

for filename in os.listdir("."):
    if filename.endswith(".jpg") and not filename.endswith("-thumb.jpg"):
        basename = filename[:-4]
        thumbname = "%s-thumb.jpg" % basename
        if os.path.exists(thumbname):
            pass
            #continue
        print "Converting %s" % filename
        # Step one: big version
        source = Image.open(filename)
        thumbnail = source.copy()
        thumbnail.thumbnail((1024, 1024))
        thumbnail.save(filename)
        # Step two: in page version
        slice = source.copy()
        w, h = slice.size
        ratio = w / float(h)
        for max_ratio, width in sizes:
            if ratio <= max_ratio:
                break
        else:
            width = sizes[-1][1]
        slice.thumbnail((width, 10000))
        slice.save(thumbname)

