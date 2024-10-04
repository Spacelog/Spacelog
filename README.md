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

However for any changes you make (fixed, new missions, or even new website features), you will want to issue a pull request to us from another [GitHub](http://github.com/) repository). In order to do that, you'll need to set up a GitHub account, and while logged in go to [our repository there](http://github.com/Spacelog/Spacelog) and hit the "fork" button (top right, near the search box). This will create a copy of Spacelog under your GitHub user; you can then grab the SSH URL (which will look like `git@github.com:<your user>/Spacelog.git`) and use for git clone, as:

    $ git clone <github SSH URL>

You can then make changes, commit them to your local copy (`git commit`), push them up to your github copy (`git push`) and finally send us a pull request (which you do via the github website). Github has some great guides to getting started with git and github linked from their homepage once you're signed in, in particular [their description of forking a repository](http://help.github.com/fork-a-repo/).

### Software to install

We strongly recommend you use [Docker](https://www.docker.com) and [Docker Compose](https://docs.docker.com/compose/) to work with Spacelog. It makes sure you're running your code in an environment that's like the real site, and doesn't require you to install dependencies manually.

You can [follow Docker's installation guide here](https://docs.docker.com/desktop/) or, if you're on a Mac, you can install with [homebrew](http://brew.sh/) by running:

```sh
brew install --cask docker
```

## Running the code

Once you have Docker (including Docker Compose) installed, you should be able to run:

```sh
docker compose up
```

That will build the Docker container, containing all the current mission content, with CSS and code re-generated as it changes. Once that command finishes (it won't exit, but it will say things like “Starting development server”), you can point your web browser at [http://dev.spacelog.org:9000/](http://dev.spacelog.org:9000/) and the global homepage should come up; from there you can navigate to other missions, which will appear at URLs such as [http://apollo11.dev.spacelog.org:9000/](http://apollo11.dev.spacelog.org:9000). The DNS is managed by us, and providing you're online everything will just work.

### The details

If you can't use Docker, or simply if you wish to know how it
all fits together under the skin, then here's the details. It's also
helpful in case you're developing the code directly, since under
certain circumstances the Django development server can crash, and
will need restarting.

We use [Overmind](https://github.com/DarthSim/overmind) to run all the components of Spacelog. Those components are:

- `global`: The Django application for the overall Spacelog project, with information about the various missions, the team, and so forth.
- `website`: The Django application for the various mission sites, including their search engines.
- `redis`: The storage that underlies both global and website, and contains all the data that those Django apps show. Redis's contents are generated when we build the Docker container, so if you change content (or want to rebuild the search index with `make reindex`, or the phase graphs with `make activity_graphs`), you need to rebuild the container (or run the relevant make commands inside your container).
- `nginx`: We proxy access to `global` and `website` through Nginx because [Fly.io](https://fly.io), where we host Spacelog, doesn't currently support multiple applications per “machine”, and [advises using nginx proxies to handle projects that support multiple domains](https://fly.io/docs/app-guides/custom-domains-with-fly/).
- `css`: In development, we also run a process to update the CSS every 10th of a second.

The commands to run these servers are in `Procfile` (or `Procfile.dev`
for development), but they mostly just call out to `Makefile` tasks

### Hosts setup for offline use

If you're not online, you can't use our development DNS, so you'll
need edit `/etc/hosts` to include an alias `dev.spacelog.org`, plus
aliases of the form `<mission>.dev.spacelog.org`, such as
`apollo13.dev.spacelog.org` and `mercury6.dev.spacelog.org`; these all
need to point to `localhost` (or to your virtual machine, if that's
how you develop things). For instance, here's an `/etc/hosts` entry
using `localhost` (put this in addition to the `localhost` line
already in there):

    127.0.0.1		apollo13.dev.spacelog.org mercury6.dev.spacelog.org dev.spacelog.org

### Reindexing

Whenever you edit information about a mission, or add a new one, you
need to reindex the content again to see it in your local environment.

If you're running in Docker (as we recommend), reindexing happens as
part of the container build process. You can manually rebuild the
container with `docker compose build` or you can have it happen
automatically as needed by rebuilding the container every time you
start your environment using `docker compose up --build` (which is a
little slower than starting a container normally, but might be easier
if you're working on missions content).

If you're running without Docker (or working inside the container
manually), you can reindex using `make reindex`.

If you get errors you may find the `lognag.pl` script in `mcshred/src`
useful: just give it some transcript files and it'll tell you where it
finds possible errors or weirdnesses. (For new missions, you'll
probably have to add things into the valid speakers list at line 71.)

Note that a full reindex can take a while (usually about 5 minutes), so
you can index just a single mission by running `python3 -m
backend.indexer MISSION_ID` (where `MISSION_ID` is the name of the
folder that the mission files are in) inside your container. If you're
not familiar with Docker containers, however, it's usually easier to do
a full container rebuild as described above.

## Deploying to production

We host Spacelog on [Fly.io](https://fly.io), and use [Cloudflare](https://www.cloudflare.com/) for DNS management, caching, and so forth. If you think you should have access to these, you probably already know who to talk to.

If you want to manage our infrastructure in Fly.io, you'll need to [install their command-line tools](https://fly.io/docs/hands-on/install-flyctl/).

The deployment configuration for Fly.io is in the `fly.toml` file. We automatically deploy changes to Fly when they are merged to `main` on GitHub, but if you need to deploy changes manually, run:

```sh
fly deploy
```

At the moment, missions' DNS and certificates are configured in Fly and Cloudflare manually, so any new mission requires a new DNS entry in Cloudflare (pointing at the IPs listed in `fly ips list`), and a new certificate (by running `fly certs add '<mission>.spacelog.org'` and adding the DNS entries it specifies to Cloudflare). In future, we plan to simplify this by using wildcard certificates and DNS for missions.

## External Source Images

We make use of external source images (which we haven't created
ourselves) in the form of:

 * .pngs of transcript PDF pages
 * Original NASA photographs

For reasons of size these aren't stored in git, they're stored in the
spacelog Amazon S3 bucket (served by Cloudfront on
http://media.spacelog.org). By default, our settings point you to this
host. If you want to test adding your own images, you can change the
`MISSIONS\_IMAGE\_URL` in `website/configs/settings.py` to serve them
locally. File a github ticket if you need images uploaded to S3.

## Adding a new mission

You'll need to create a directory in `missions`. For Mercury-Redstone
missions these should start `mr`, for Mercury-Atlas `ma`, for Gemini
they start just `g` and for Apollo `a`. If anyone wants to do non-NASA
missions, or Shuttle missions, then get in touch and we'll figure out
a naming convention.

Look in `transcript-file-format` for a description of how we lay out
files. If you're transcribing a mission we don't have, you will find
the example `_meta` and `TEC` files useful, since they are the main
two files you'll need to create (if you're going to include more than
just the air-to-ground transcription, you'll want to put that in
`TEC`, the command module transcript in `CM`, and so on). If you can
make them in that format (or get as close as you can), and send them
through to us along with a link to the original transcript PDFs you
used, we'll do the rest. (If you are gifted in design, the source
files for all the artwork we've created is available, although we
haven't yet put it online -- yell if you need it as a basis for making
things like orbital diagrams.)

### Images

The mission images folder (eg `missions/a11/images`) contains a number
of images in standard locations and of standard sizes. This is an
incomplete list. There are Photoshop templates available to help with
constructing some of these (talk to the mailing list to get hold of
them).

 * `badge.png` (200 pixels wide, square-ish) and `badge_thumb.png` (40x40
   pixels): the mission patch, with a transparent background, designed
   for use on a dark background
 * `avatars/` contains images for each character in the transcript, in
   one of the following forms:
     * transcript name: `F.png`, `IWO_48.png`
     * ground crew or similar: `capcom_generic.jpg`, `charlie_duke.png`, `nixon.png`, in black and white (ideally in shirt sleeves)
     * astronauts in flight: `aldrin.jpg`, `armstrong.jpg`, in black and white with a yellow filter applied (ideally in a spacesuit)
     * `blank_avatar_48.png` (default blank avatar)

   See [the relevant wiki page](https://github.com/spacelog/spacelog/wiki/avatars) for some helpful pre-built avatars.
 * `people/` contains images used on the people page, for characters in
   the transcript we call out, which are constructed based on their `role`.
   The three role groups should have consistent sizes, typically up to
   200 pixels wide and 150-200 pixels high (there's a fair amount of
   flexibility here, although 190x205 for the first two and 190x155 for
   the others was the original design).
     * `astronaut`: in colour (if possible); the aim is to get them in
       spacesuits or flight suits, although this isn't always possible
     * `mission-ops-title`: black and white (on the same page as
       astronauts; we generally include CAPCOM and Flight there as
       separate "characters" to explain these key roles, with people filling
       them or otherwise interesting to the mission as `mission-ops`)
     * `mission-ops` black and white (on another page)
 * a number of directories for images for each act, the details of
   which are managed in the`_meta` file's `acts` section, so can be anything,
   but are generally `act1.jpg` or `act1.png` etc
     * `banners/`: 1020x200 pixels, used as headers within the transcript
     * `illustration/`: 950-960 by 300-330 pixels, optional orbital
       diagram with spacecraft schematic (but could skip the orbital
       diagram eg for Apollo 9), used on the phases page
     * `orbital/`: 956x104 pixels, optional orbital diagram (only
       makes sense for moon missions), used in the expanded transcript
       footer
     * `homepage/`: 220x140 pixels, used on the mission homepage
       * This directory also contains a single `background.jpg`, which
         should be dark, and probably feathered toward the right and
         bottom edges. Size should be "large", but there are no
         particular dimensions or range of dimensions. Choose
         something that looks good.

### Memorials

For missions that resulted in fatalities, we do not aim to provide a
regular site with a transcript. Instead, we can provide a small
"memorial" site, controlled entirely from the `_meta` file. Set the
`memorial` key to `true`, and the following keys will be used:

 * `name`, `subdomains`, `featured`, `incomplete` as normal
 * `utc_launch_time` is used for ordering on the Spacelog homepage
 * `characters` should contain only the astronauts, with:
   * `name`, `mission_position`, `bio`
   * `photo`, `photo_width` and `photo_height`
   * `role` of `"astronaut"`
   * optional `quote`, and optional `quote_url`
   * characters in memorials should not have stats
 * `copy` with:
   * `title`, `upper_title`, `lower_title`, `description`, `summary`
   * `narrative` (main body for memorial page, doesn't support HTML,
     should be a list of strings, each of which forms a paragraph)
   * `image_attributions` should contain details of the crew photo
     (`url`, `title`, `attrib_url`, `attrib` and `license`) unless it
     is public domain (which it usually will be)

Images (eg in `missions/a1/images/`) that should be in place are:

 * `badge_thumb.png`, `badge.png` (principally for sharing)
 * astronaut photos in `people/` (typically official NASA headshots)
 * `homepage/crew.jpg` (ideally a photo of the entire crew in training),
   should be "large" (as `homepage/background.jpg`, but more foregroundy);
   on large screens it will be shown at 960px wide, and on narrower at
   full bleed (so on high density screens up to 1920px may be used)


### Multiple transcripts

As noted above in the information for non-technical folk, if you clean
up multiple different transcripts for a single mission (for instance
you might do not only the TEC ("technical" ground-to-air) recording
but also the CM and/or LM recordings), then please keep them in
separate files rather than merging them.

## Technical glossary

Within the system, there are a number of terms that describe pieces of
the system but do not necessarily match what is shown on the websites.

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

## Characters

Characters are defined in a _meta key `characters`, which is a
dictionary with keys the character identifiers in the transcript and
values a further dictionary of information about that character. For
instance:

    {
        "characters": {
            "P": {
                "role": "astronaut",
                "name": "Virgil Ivan Grissom",
                "short_name": "Gus Grissom",
                "mission_position": "Pilot",
                "bio": "A few sentence biography",
                "photo": "grissom.jpg",
                "photo_width": 190,
                "photo_height": 205,
                "avatar": "grissom.jpg"
            }
        }
    }

This defines the character P. `bio`, `photo` (stored in the mission's
`images/people` directory; `photo_width` / `photo_height` should be
set appropriately) are used on the people page.

`role` is based on initial usage, and so can be a little confusing. It
should be one of astronaut, mission-ops, mission-ops-title or other
(defaulting to other). Astronaut means a full-size, prominent place on
the main people page (190x205 image with biography as above, and also
support for stats and a quote); mission-ops-title will get a less
prominent position on the main people page (190x205 with biography);
mission-ops go on a second page (linked as "View Mission Control Team"
from the main people page), where they get a 190x155 photo and brief
biography.

When dealing with translations, you can also set the role to any of
the above with '-alias' at the end (eg astronaut-alias,
mission-ops-title-alias) and explicitly match the `slug` to the "real"
character definition. Transcripts will show details from the alias
(including `short_name` and `avatar`, but will link via the explicit
slug to the "real" biography on the relevant people page, assuming
there is one).

The people pages show the full name (the `name` key) and the mission
position from the character definition. The short name is shown within
the transcript, with the avatar (48x48, stored in the mission's
`images/avatars` directory; astronauts get a yellow hue to
differentiate them from those not in space during the mission)
alongside.

### Character stats and quotes

Characters with a role of "astronaut" can optionally have statistics
and quotes, as shown below:

    {
        "characters": {
            "CDR": {
              "role": "astronaut",
              "name": "James A. (Jim) Lovell, Jr.",
              "short_name": "Jim Lovell (CDR)",
              "mission_position": "Commander",
              "bio": "...",
              "photo": "lovell.png",
              "photo_width": 190,
              "photo_height": 205,
              "avatar": "jim_lovell.jpg",
              "stats": [
                {
                    "value": 715,
                    "text": "hours in space"
                },
                {
                    "value": 4,
                    "text": "missions"
                },
                {
                    "value": 42,
                    "text": "age at launch"
                }
              ],
              "quotable_log_line_id": "TEC:05:18:04:46"
            }
        }
    }

The quote must be in the transcript, and is given as the transcript
name followed by the GET of the logline. (This means you can't use
loglines that have multiple speakers.)

There should be three stats, and you will likely have to juggle things
around in order to make them fit the layout. We haven't used stats on
all missions; it isn't always possible to find suitable figures for
the astronauts involved.

### The shift system

On longer missions, generic positions such as CAPCOM or F (flight
director) are shared between several people operating in shifts. This
is done by having a character dictionary key of `shifts`, whose value
is a list of two element lists:

    {
        "characters": {
            "STONY": {
              "role": "other",
              "name": "Blockhouse Comm",
              "short_name": "Stony",
              "shifts": [
                [ "DEKE_SLAYTON", "00:00:00:00" ]
              ]
            }
        }
    }

This means that the first shift is taken by the character with
identifier DEKE_SLAYTON, at GET 00:00:00:00. Since identifying shifts
at this remove from the event isn't always straightforward, there will
often be a third element in the list giving an annotation,
justification or source:

    {
        "characters": {
            "CC": {
                "role": "mission-ops-title",
                "name": "Capsule Communicator",
                "short_name": "CapCom",
                "bio": "...",
                "photo": "capcom.jpg",
                "photo_width": 190,
                "photo_height": 205,
                "avatar": "capcom_generic.png",
                "shifts": [
                  ["JOE_KERWIN", "-00:01:00:00", "strictly, only Kerwin, Brand and Lousma were taking shifts (AFAICT), however other astronauts come on as CAPCOM in the original transcript, and we use the shift mechanism to display that properly"],
                  ["JOHN_YOUNG", "00:04:39:01", "identified by PAO transcript"],
                  ["JOE_KERWIN", "00:04:50:45"],
                  ["VANCE_BRAND", "00:07:09:09"],
                  ["JACK_LOUSMA", "00:16:00:00", "uncertain (and moot) since he doesn't appear in the transcript at this point"]
                ]
            }
        }
    }

We also (as in the first example above, from Gus Grissom's
Mercury-Redstone 4 flight) use the shift system to "delegate" a
generic character (such as STONY, the callsign for an astronaut
communicator in the blockhouse during Mercury launches) to a specific
character (in this case Deke Slayton) who served in that role for the
mission in question.

## Glossary

Glossary terms are defined in a dictionary from identifier (used in
the transcripts) to an object with a number of (mostly optional)
attributes. Missions can bring in shared glossaries (in
``missions/shared/glossary/``) by having a ``_meta`` key of
``shared__glossaries`` containing a list of shared glossary names. They
also have a per-mission glossary, in the ``_meta`` key ``glossary``.

The following attributes are available to a glossary entry:

 * ``type``: "abbreviation" or "jargon" (the latter is the default)
 * ``links``: a list of objects (with ``url`` and ``caption`` attributes); currently not used
 * ``summary``: short definition, typically the expansion for abbreviations
 * ``description``: optional more detailed description of the term (for instance, "Drogue" is a glossary entry, with summary "Drogue parachute", and a description which explains what the drogues' purpose is)
 * ``description_lang``, ``summary_lang`` and ``abbr_lang`` set the language code if not ``en-us``

Glossary entries are referred to in transcripts (strictly in anything
run through "linkify", which is also used for things like character
biographies and quotes -- notably this includes glossary
descriptions). Just do something like the following:

```
[glossary:term]
[glossary:term|display]
```

The second form allows you to use a glossary entry while using
different display text. (Particularly useful if dealing with
translations, since the glossary terms themselves will be in one
language.)

Note that unless there's a description, the transcript won't link to
the glossary, it'll just provide a title hover giving the glossary
item summary.

The glossary page for each mission starts with the ``glossary_introduction``
copy key in ``_meta``.

## Time links

Similar to glossary references, parsed text can contain references to
other parts of the mission. This is done using a time link, of the
form `[time:TIME]` or `[time:TIME|display]`. The link time may be
abbreviated (it's filled up to the four time components on the left
with zeros, so if you use `[time:02:15]` the system will treat that as
`[time:00:00:02:15]`. The link time must use colons as separators,
although the transcript text may not: `[time:02:42:08|02 42 07]`.

## Code layout

The main code is two Django projects and a python library for managing
transcript files into a redis data store. There is also a directory
full of per-mission information (transcript files, images and so on),
and some other tools directories.

 * `website/` runs the per-mission websites (Django project)
 * `global/` runs the project global homepage (Django project)
 * `backend/` (python library to load transcript files into redis/xappy, generate stats images, and provide an API for accessing streams and other information)
 * `transcript-file-format/` (documentation of the transcript file format)
 * `missions/` contains the per-mission data, particularly the transcript files and meta file, but also images and so forth
 * `tools/` (standalone python tools)
 * `mcshred/` (python and perl programs for dealing with OCR data from NASA PDFs)
 * `ext/` (historical mechanism used during development because `pip` doesn't work in forts)
