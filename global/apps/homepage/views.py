# -*- encoding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_control
from urllib import quote
import random
from backend.api import Mission

AFFILIATE_CODES = {'us': 'spacelog-20', 'uk': 'spacelog-21'}

READING_LISTS = [
    ("By astronauts and cosmonauts",
        [
            ("Deke!",           "Deke Slayton with Michael Cassutt",    "031285918X"),
            ("We Seven",        "The Mercury Astronauts",               "1439181039"),
            ("We Have Capture", "Tom Stafford with Michael Cassutt",    "1588341011"),
            ("Two Sides of the Moon", "David Scott and Alexei Leonov",  "0312308663"),
        ]),
    ("By other principals",
        [
            ("Flight",          "Chris Kraft",                          "B000EXYZR2"),
            ("Project Mars: A Technical Tale", "Wernher von Braun",     "0973820330"),
        ]),
    ("Other books",
        [
            ("Full Moon",       "Michael Light",                        "0375406344"),
        ])
]

class Thing:
    def __init__(self, quote, snippet, url, source, date):
        self.quote = quote
        self.snippet = snippet
        self.url = url
        self.source = source
        self.date = date

NICE_THINGS = [
    Thing(
        "What could possibly be cooler…gorgeous, elegant and easy-to-use",
        "What could possibly be cooler?",
        "http://techland.time.com/2011/05/11/site-built-in-a-fort-lets-you-scan-pivotal-space-tales/",
        "time.com",
        "11 May, 2011",
    ),
    Thing(
        "Seriously cool.",
        "Seriously cool",
        "https://techcrunch.com/2011/05/07/did-devfort-just-hand-over-astronaut-listening-data-to-the-www/",
        "TechCrunch",
        "7 May, 2011",
    ),
  
    Thing(
        "Spacelog is awesome.", 
        "Spacelog is awesome", 
        "https://www.rockpapershotgun.com/2010/12/05/the-sunday-papers-148/", "Rock, Paper, Shotgun", "5 Dec, 2010",
    ),

    Thing(
        "This is the kind of historical documentation and access that reminds us of why the internet is so, insanely awesome.", 
        "Reminds us the internet is so, insanely awesome",
        "https://www.engadget.com/2010/12/02/spacelog-provides-fascinating-searchable-text-transcripts-for-na/", "Engadget", "2 Dec, 2010",
    ),

    Thing(
        "&hellip;highly addictive&hellip;", 
        "&hellip;highly addictive&hellip;", 
        "https://www.huffingtonpost.com/2010/12/02/spacelogorg-nasa-mission-transcripts_n_790735.html", "The Huffington Post", "2 Dec, 2010",
    ),

    Thing(
        "[Spacelog] is the best thing ever on the internet!", 
        "[Spacelog] is the best thing ever on the internet!", 
        "https://twitter.com/moleitau/status/9930034542288896", "Matt Jones", "1 Dec, 2010",
    ),

    Thing(
        "Wonderful stuff.", 
        "Wonderful stuff", 
        "https://kottke.org/10/12/spacelog", "Jason Kottke", "1 Dec, 2010",
    ),

    Thing(
        "I absolutely love this. Spacelog.org is taking the radio transcripts from NASA missions, pairing them with great graphic design, and making the whole thing searchable and linkable. The result: A delightfully immersive perspective on history.", 
        "A delightfully immersive perspective on history",
        "https://boingboing.net/2010/12/01/an-interactive-histo.html", "Boing Boing", "1 Dec, 2010",
    ),

    Thing(
        "If this isn’t making content meaningful, accessible (in a traditional sense), and enjoyable to consume, I don’t know what is.",
        "Meaningful, accessible and enjoyable",
        "http://cameronmoll.tumblr.com/post/2060251631/spacelog", "Cameron Moll", "1 Dec, 2010",
    ),
]

def homepage(request):
    missions = [
        mission for mission in list(Mission.Query(request.redis_conn))
        if not mission.incomplete
    ]
    missions_coming_soon = [
        mission for mission in list(Mission.Query(request.redis_conn))
        if mission.incomplete and mission.featured
    ]
    return render_to_response(
        'homepage/homepage.html',
        {
            'missions': missions,
            'missions_coming_soon': missions_coming_soon,
            'quote': random.choice(NICE_THINGS),
        },
    )

def _get_amazon_url(country_code, asin):
    if country_code.lower() == 'uk':
        domain = 'co.uk'
        code = AFFILIATE_CODES['uk']
    else:
        domain = 'com'
        code = AFFILIATE_CODES['us']
    url = "https://www.amazon.%s/dp/%s" % (domain, asin)
    link_string = "https://www.amazon.%s/gp/redirect.html?ie=UTF8&location=%s&tag=%s" % \
            (domain, quote(url, safe=''), code)
    return link_string

def _get_image_url(asin):
    return "http://images.amazon.com/images/P/%(asin)s.01.THUMBZZZ.jpg" % {
        'asin': asin,
    }

def _get_reading_list(country_code):
    reading_list = []
    for category, books in READING_LISTS:
        books_new = []
        for title, author, asin in books:
            books_new.append((title, author, _get_amazon_url(country_code, asin), _get_image_url(asin)))
        reading_list.append((category, books_new))
    return reading_list

@cache_control(no_cache=True)
def about(request):
    country_code = request.META.get('HTTP_CF_IPCOUNTRY')
    if country_code is None:
        country_code = request.META.get(
            'GEOIP_COUNTRY_CODE',
            '--',
        )

    # Fetch the list of contributors from the various missions. Use a
    # set() because we only want to list each contributor once.
    contributors = set()
    for mission in list(Mission.Query(request.redis_conn)):
        if not mission.incomplete:
            contributors = contributors | set(mission.copy.get('cleaners', []))
    # Some people have contributed code changes but haven't worked on
    # missions.
    contributors = contributors | {
        'Adam Johnson',
        'Tom Morris',
        'Christopher Stumm',
    }

    # Strip out any of the original team, because they're already
    # listed explicitly.
    contributors = contributors - {
        'Matthew Ogle',
        'Russ Garrett',
        'Hannah Donovan',
        'Chris Govias',
        'Gavin O\'Carroll',
        'Ryan Alexander',
        'James Aylett',
        'George Brocklehurst',
        'David Brownlee',
        'Ben Firshman',
        'Mark Norman Francis',
        'Andrew Godwin',
        'Steve Marshall',
    }

    def _sort(element):
        return element.split(' ')[-1]
    contributors = sorted(contributors, key=_sort)

    # Finally, we have websites for some of these (but we don't use
    # that on the mission cleaners list).
    def _as_dict(contributor):
        ret = {
            'name': contributor,
        }
        url = {
            'Emily Carney': 'https://this-space-available.blogspot.com/',
            'Adam Johnson': 'https://pkqk.net',
            'Tom Morris': 'https://tommorris.org',
            'Matthew Somerville': 'http://www.dracos.co.uk',
            'Christopher Stumm': 'http://stumm.ca/',
        }.get(contributor)
        if url is not None:
            ret['website'] = url
        return ret

    contributors = [ _as_dict(contributor) for contributor in contributors ]

    return render_to_response(
        'pages/about.html',
        {
            'READING_LISTS': _get_reading_list(country_code),
            'contributors': contributors,
            'page': 'about',
        },
    )

@cache_control(no_cache=True)
def press(request):
    return render_to_response(
            'pages/press.html',
            {
                'page': 'press',
                'NICE_THINGS': NICE_THINGS,
            },
            )

@cache_control(no_cache=True)
def get_involved(request):
    return render_to_response(
            'pages/get-involved.html',
            {'page': 'get-involved'},
            )
