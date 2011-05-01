# Spacelog

This is the source code for [Spacelog](http://spacelog.org/), a website for experiencing space missions through radio transcripts and photography.

With the exception of the font and some icons (credited on the mission about page), everything outside the `missions` directory is released under the [CC-0](http://creativecommons.org/publicdomain/zero/1.0/) license. Mission images are credited in the mission's `_meta` file.

We hope you have fun with this -- we have!

[The Spacelog team](mail:spacelog@googlegroups.com)



# Getting involved without technical knowledge

## Correcting minor errors

For small errors (whether transcription errors, or something like spelling mistakes on the rest of the site), it's probably easiest to just email them through to us at [spacelog@googlegroups.com](mail:spacelog@googlegroups.com).

## Helping transcribe a new mission

If you [download the PDFs from NASA](http://www.jsc.nasa.gov/history/mission_trans/mission_transcripts.htm) for a mission you want to add, you'll discover that you can select text in them and copy it out into a text editor, or something like OpenOffice Writer, Apple's Pages or Microsoft Word. You'll see lots of lines that look like this:

    02 07 55 20 CMP I believe we've had a problem here.

However some of the lines will have errors (from the small, such as `O` instead of `0`, to the large such as entire lines being completely garbled). If you go back to the PDF, you can usually quite easily figure out what was originally typed out but which the automatic OCR didn't get right.

There are also some non-dialogue lines. These should all be indented by a single tab; the most important ones are:

        TAPE 2/1
        PAGE 9

which happen at the start of a new page of the PDF. In this case they mean that it's the first page of the transcript of tape 2, and is page 9 of the complete transcript. We particularly need the page number so we can link back to the original typescript in the site.

If you clean up the text version like this, and send it through to us, we can do the rest (although it may take us a bit of time). Since some of the missions are quite long (hundreds of pages of transcript), you may want to share the load between a group. Whether you do that or decide to go it alone, it'd be great if you could let us know at at [spacelog@googlegroups.com](mail:spacelog@googlegroups.com) what you're working on, so we can help you out, and make sure you don't duplicate others' effort.

### A quick note about multiple transcripts

For Mercury-Atlas 6, there is only one transcript available, that of the air-to-ground radio communications (John Glenn's mike was hot through the entire mission). For Apollo 13, there is a second transcript from the Command Module recording, but it cuts out very early into the mission, so we didn't consider it worth including.

However for many other missions there are multiple transcripts. If you're adding missions to Spacelog, please keep these transcripts in different files. We don't yet have support to identify them distinctly, but if you move them all into one big file it'll be impossible for us ever to work on that!

# Getting involved with technical knowledge

## Getting set up

### Source code

Clone the repository from git:

    $ git clone git://github.com/Spacelog/Spacelog.git

For any changes you make (fixed, new missions, or even new website features), you can issue a pull request to us from another [github](http://github.com/) repository).

### Software to install

 * python (and pip)
 * redis (often packages as `python-redis`; we need Redis 2.0 or later)
 * imagemagick and optipng (for stats images on the phase pages)
 * Xapian and its python bindings (the search engine library we use; often packaged as `python-xapian`)
 * `CSS::Prepare` (a perl library for managing CSS; `sudo cpanm -f CSS::Prepare`; if you don't have `cpanm` there are [straightforward installation instructions](http://search.cpan.org/~miyagawa/App-cpanminus-1.1004/lib/App/cpanminus.pm#INSTALLATION) available)
 * various python modules (run `pip install -r requirements.txt`)

The easiest way to grab the python modules may be to build a `virtualenv` in the Spacelog checkout:

	virtualenv ENV
	ENV/bin/pip install -r requirements.txt

then use `ENV/bin/python` where normally you'd use just `python`. (If it's recent enough, `virtualenv` may install a script to "activate" its copy of python in your shell, which you run as `source ENV/bin/activate`, or `ENV/Scripts/activate.bat` on Windows.)

#### A word of caution

We are currently locked to a specific version of Django, because we use 1.3 features but the release itself has a bug which prevents us from using it in development. Once there's a stable release of Django without this problem we'll move off this.

## Running the code

If you have `screen` installed and are using a virtualenv as above, you should be able to just run `make screen` to get everything running for you. You also need to run `make reindex` to load all the details of the missions. Then you can point your web browser at [http://dev.spacelog.org:8001/](http://dev.spacelog.org:8001/) and the global homepage should come up; from there you can navigate to other missions, which will appear at URLs such as [http://apollo11.dev.spacelog.org:8000/](http://apollo11.dev.spacelog.org:8000). The DNS is managed by us, and providing you're online everything will just work.

`make screen` fires up an instance of `screen`, which is an easy way of running multiple programs on one terminal. Currently it leaves you looking at the development server log for the global homepage, but you can switch to a blank terminal by typing `^A 0`, ie: holding down the `ctrl` key, pressing `A`, releasing `ctrl` and then pressing `0`. This is a good place to run `make reindex` from.

All our `make` commands will take care of the virtualenv for you; if you're not using one, you can use `PYTHON=python make <whatever>` instead.

### The details

If you can't use `make screen`, or simply if you wish to know how it all fits together under the skin, then here's the details. It's also helpful in case you're developing the code directly, since under certain circumstances the Django development server can crash, and will need restarting. Similarly if you add a new CSS file, you will currently have to restart the appropriate devcss server.

We use redis for storage, so you need to have `redis-server` running before you run `make reindex` in the checkout directory, which will import all the mission data into redis. You may also want to do `make statsporn` to build the graphs for the phases page of how much was said at different times (and, in case we've added more graphs but haven't updated this, *other things* :-).

You then need to have some other servers running on top of redis:

 * `make devcss` will run `CSS::Prepare` in development mode, so changes to CSS files will be reflected automatically
 * `make devcss_global` will run `CSS::Prepare` for the project homepage
 * `make devserver` will run the mission-specific websites; if not using a `virtualenv`, `PYTHON=python make devserver` should do the trick
 * `make devserver_global` will run the project homepage; if not using a `virtualenv`, `PYTHON=python make devserver_global` should do the trick

### Hosts setup for offline use

If you're not online, you can't use our development DNS, so you'll need edit `/etc/hosts` to include an alias `dev.spacelog.org`, plus aliases of the form `<mission>.dev.spacelog.org`, such as `apollo13.dev.spacelog.org` and `mercury6.dev.spacelog.org`; these all need to point to `localhost` (or to your virtual machine, if that's how you develop things). For instance, here's an `/etc/hosts` entry using `localhost` (put this in addition to the `localhost` line already in there):
  
    127.0.0.1		apollo13.dev.spacelog.org mercury6.dev.spacelog.org dev.spacelog.org

and here's one for a virtual machine (you'll need to change the dotted quad at the start of the line):
  
    192.168.56.101	apollo13.dev.spacelog.org mercury6.dev.spacelog.org dev.spacelog.org

### Reindexing

Whenever you edit information about a mission, or add a new one, you need to run `make reindex` again. If you get errors you may find the `lognag.pl` script in `mcshred/src` useful: just give it some transcript files and it'll tell you where it finds possible errors or weirdnesses. (For new missions, you'll probably have to add things into the valid speakers list at line 71.)

Note that a full `make reindex` can take a while, so you can index just a single mission by doing `ENV/bin/python -m backend.indexer ma6` or similar (or just `python -m backend.indexer ma6` if you aren't using a virtualenv.

## External Source Images

We make use of external source images (which we haven't created ourselves) in the form of:

* .pngs of transcript PDF pages
* Original NASA photographs

For reasons of size these aren't stored in git, they're stored in the spacelog Amazon S3 bucket (served by Cloudfront on http://media.spacelog.org). By default, our settings point you to this host. If you want to test adding your own images, you can change the MISSIONS\_IMAGE\_URL in `website/configs/settings.py` to serve them locally. File a github ticket if you need images uploaded to S3.

## Adding a new mission

You'll need to create a directory in `missions`. For Mercury-Redstone missions these should start `mr`, for Mercury-Atlas `ma`, for Gemini they start just `g` and for Apollo `a`. If anyone wants to do non-NASA missions, or Shuttle missions, then get in touch and we'll figure out a naming convention.

Look in `transcript-file-format` for a description of how we lay out files. If you're transcribing a mission we don't have, you will find the example `_meta` and `TEC` files useful, since they are the main two files you'll need to create (if you're going to include more than just the air-to-ground transcription, you'll want to put that in `TEC`, the command module transcript in `CM`, and so on). If you can make them in that format (or get as close as you can), and send them through to us along with a link to the original transcript PDFs you used, we'll do the rest. (If you are gifted in design, the source files for all the artwork we've created is available, although we haven't yet put it online -- yell if you need it as a basis for making things like orbital diagrams.)

### Multiple transcripts

As noted above in the information for non-technical folk, if you clean up multiple different transcripts for a single mission (for instance you might do not only the TEC ("technical" ground-to-air) recording but also the CM and/or LM recordings), then please keep them in separate files rather than merging them.

## Technical glossary

Within the system, there are a number of terms that describe pieces of the system but do not necessarily match what is shown on the websites.

 * TRANSCRIPT FILE -- our textual representation of the original transcript; see `transcript-file-format/TEC` for a commented example
 * TIMESTAMP -- four colon-separated numbers that represent the GET (Ground Elapsed Time), the time since launch within the mission; the four numbers are days, hours, minutes, seconds, so ignition is 00:00:00:00; these are used in the transcript files, and also in URLs
 * LOG LINE -- smallest linkable chunk, identified by timestamp and transcript file
 * RANGE -- a range between two timestamps (can be the same two)
 * LABEL -- a keyword applied to a range within a specific stream (note that labels are not currently used)
 * META FILE -- a per-mission file called `_meta` that contains information such as glossary items, pull quotes for the homepage, and acts (see `transcript-file-format/_meta` for a commented example
 * CHARACTER -- a speaker who appears in a transcript file; additional information about them appears in the meta file
 * SHIFT -- a range where one "role" character (such as CAPCOM or the flight director) can be identified with a "real" character (such as Charlie Duke or Deke Slayton); ranges are defined in the meta file

From this we generate a number of higher-level pieces which are used in the website.

 * ACT -- an editorially defined range that represents a segment of the mission, which may for instance reference orbital mechanics (in the websites these are referred to as phases)
 * KEY SCENE -- an editorially defined point in the transcript where an important event or exchange starts
 * STREAM -- a collection of related content arranged on a timeline

## Code layout

The main code is two Django projects and a python library for managing transcript files into a redis data store. There is also a directory full of per-mission information (transcript files, images and so on), and some other tools directories.

 * `website/` runs the per-mission websites (Django project)
 * `global/` runs the project global homepage (Django project)
 * `backend/` (python library to load transcript files into redis/xappy, generate stats images, and provide an API for accessing streams and other information)
 * `transcript-file-format/` (documentation of the transcript file format)
 * `missions/` contains the per-mission data, particularly the transcript files and meta file, but also images and so forth
 * `tools/` (standalone python tools)
 * `mcshred/` (python and perl programs for dealing with OCR data from NASA PDFs)
 * `ext/` (historical mechanism used during development because `pip` doesn't work in forts)
