# Spacelog

This is the source code for [Spacelog](http://spacelog.org/), a website for experiencing space missions through radio transcripts and photography.

With the exception of the font and some icons (credited on the mission about page), everything outside the `missions` directory is released under the [CC-0](http://creativecommons.org/publicdomain/zero/1.0/) license. Mission images are credited in the mission's `_meta` file.

# A quick note about multiple transcripts

For Mercury-Atlas 6, there is only one transcript available, that of the air-to-ground radio communications (John Glenn's mike was hot through the entire mission). For Apollo 13, there is a second transcript from the Command Module recording, but it cuts out very early into the mission, so we didn't consider it worth including.

However for many other missions there are multiple transcripts. If you're adding missions to Spacelog, please keep these transcripts in different files. We don't yet have support to identify them distinctly, but if you move them all into one big file it'll be impossible for us ever to work on that!

# Getting involved without technical knowledge

For small errors, it's probably easiest to just email them through to us at [spacelog@googlegroups.com](mail:spacelog@googlegroups.com).

For anything larger, we'd rather you send us corrected files from the `missions` directory. Look in `transcript-file-format` for a description of how we lay out files. If you're transcribing a mission we don't have, you will find the example `_meta` and `TEC` files useful, since they are the main two files you'll need to create (if you're going to include more than just the air-to-ground transcription, you'll want to put that in `TEC`, the command module transcript in `CM`, and so on). If you can make them in that format (or get as close as you can), and send them through to us along with a link to the original transcript PDFs you used, we'll do the rest. (If you are gifted in design, we've included the source files for all the artwork we've created, which you could use as a basis for making things like orbital diagrams.)

If that's too hard for you, we can import from a much simpler file format based on the automatic OCR text version that NASA includes in their original transcript PDFs. If you select all the text of a transcript PDF and copy it into a text editor, you'll see lots of lines that look like this:

    02 07 55 20 CMP I believe we've had a problem here.

However some of the lines will have errors (from the small, such as `O` instead of `0`, to the large such as entire lines being completely garbled). If you go back to the PDF, you can usually quite easily figure out what was originally typed out but which the automatic OCR didn't get right.

There are also some non-dialogue lines. These should all be intended by a single tab; the most important ones are:

        TAPE 2/1
        PAGE 9

which happen at the start of a new page of the PDF. In this case they mean that it's the first page of the transcript of tape 2, and is page 9 of the complete transcript. We particularly need the page number so we can link back to the original typescript in the site.

If you clean up the text version like this, and send it through to us, we can do the rest (although obviously it will take longer than if you also create a `_meta` for us).

# Getting involved with technical knowledge

Clone the repository:

    $ git clone git://github.com/Spacelog/Spacelog.git

and you can run the entire system locally. For any changes you make (fixed, new missions, or even new website features), you can issue a pull request to us from another [github](http://github.com/) repository). You will need some software installed:

 * python (and pip)
 * redis (often packages as `python-redis`; we need Redis 2.0 or later)
 * imagemagick (for stats images on the phase pages)
 * Xapian and its python bindings (the search engine library we use; often packaged as `python-xapian`)
 * `CSS::Prepare` (a perl library for managing CSS; `sudo cpanm -f CSS::Prepare`)
 * various python modules (run `pip install -r requirements.txt`)

Make sure `redis-server` is running, then run `make reindex` in the checkout directory, which will import all the mission data into redis. You then need to have three other servers running:

 * `make devcss` will run `CSS::Prepare` in development mode (so changes to CSS files will be reflected automatically)
 * `python website/manage.py runserver 0.0.0.0:8000` will run the mission-specific websites
 * `python global/manage.py runserver 0.0.0.0:3000` will run the project homepage

To make it possible to work with multiple missions, you need edit `/etc/hosts` to include an alias `artemis`, plus aliases of the form `<mission>.artemis`, such as `apollo13.artemis` and `mercury6.artemis`; these all need to point to `localhost` (or to your virtual machine, if that's how you develop things). For instance, here's an `/etc/hosts` entry using `localhost`:
  
    localhost	apollo13.artemis mercury6.artemis artemis

and here's one for a virtual machine (you'll need to change the dotted quad at the start of the line):
  
    192.168.56.101	apollo13.artemis mercury6.artemis artemis

The project homepage will appear at [http://artemis:3000/](http://artemis:3000/), and the per-mission sites at [http://apollo13.artemis:8000/](http://apollo13.artemis:8000/) (which will show the Apollo 13 mission), [http://mercury6.artemis:8000/](http://mercury6.artemis:8000/) (Mercury-Atlas 6) and so on.

Whenever you edit information about a mission, or add a new one, you need to run `make reindex` again.

## Technical glossary

Within the system, there are a number of terms that describe pieces of the system but do not necessarily match what is shown on the websites.

 * TRANSCRIPT FILE -- our textual representation of the original transcript; see transcript-file-format/
 * TIMESTAMP -- four colon-separated numbers that represent the GET (Ground Elapsed Time), the time since launch within the mission; the four numbers are days, hours, minutes, seconds, so ignition is 00:00:00:00; these are used in the transcript files, and also in URLs
 * LOG LINE -- smallest linkable chunk, identified by timestamp and transcript file
 * RANGE -- a range between two timestamps (can be the same two)
 * LABEL -- a keyword applied to a range within a specific stream (note that labels are not currently used)

From this we generate a number of higher-level pieces which are used in the website.

 * ACT -- an editorially defined range that represents a segment of the mission, which may for instance reference orbital mechanics (in the websites these are referred to as phases)
 * KEY SCENE -- an editorially defined point in the transcript where an important event or exchange starts
 * STREAM -- a collection of related content arranged on a timeline

## Original transcript pages

The system has the capability to display the original scanned NASA transcripts, but these files aren't included in the repository for reasons of size. These images are only required for displaying the original transcript pages.

[This tarball](http://s3.amazonaws.com/spacelog/original-images.tar) contains these files. Place it in the repository root and untar it, and it'll put these files in the right places.

## Code layout

The main code is two Django projects and a python library for managing transcript files into a redis data store. There is also a directory full of per-mission information (transcript files, images and so on), and some other tools directories.

 * `website/` runs the per-mission websites (Django project)
 * `global/` runs the project global homepage (Django project)
 * `backend/` (python library to load transcript files into redis/xappy, generate stats images, and provide an API for accessing streams and other information)
 * `transcript-file-format/` (documentation of the transcript file format)
 * `missions/` contains the per-mission data, images and so on
 * `tools/` (standalone python tools)
 * `mcshred/` (python and perl programs for dealing with OCR data from NASA PDFs)
 * `ext/` (historical mechanism used during development because `pip` doesn't work in forts)
