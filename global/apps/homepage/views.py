# -*- encoding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_control
from urllib import quote
import collections
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

Thing = collections.namedtuple("Thing", [ 'quote', 'url', 'source', 'date' ])
NICE_THINGS = [
    Thing(
        "A must-visit site for space enthusiasts.", 
        "http://www.komando.com/coolsites/index.aspx?id=10587", "Kim Komando Cool Site of the Day",  "11 Apr, 2011",
    ),
  
    Thing(
        "Spacelog is awesome.", 
        "http://www.rockpapershotgun.com/2010/12/05/the-sunday-papers-148/", "Rock Paper, Shotgun", "5 Dec, 2010",
    ),

    Thing(
        "This is the kind of historical documentation and access that reminds us of why the internet is so, insanely awesome.", 
        "http://www.engadget.com/2010/12/02/spacelog-provides-fascinating-searchable-text-transcripts-for-na/", "Engadget", "2 Dec, 2010",
    ),

    Thing(
        "&hellip;highly addictive&hellip;", 
        "http://www.huffingtonpost.com/2010/12/02/spacelogorg-nasa-mission-transcripts_n_790735.html", "The Huffington Post", "2 Dec, 2010",
    ),

    Thing(
        "[Spacelog] is the best thing ever on the internet!", 
        "http://twitter.com/moleitau/status/9930034542288896", "Matt Jones", "1 Dec, 2010",
    ),

    Thing(
        "Wonderful stuff.", 
        "http://kottke.org/10/12/spacelog", "Jason Kottke", "1 Dec, 2010",
    ),

    Thing(
        "I absolutely love this. Spacelog.org is taking the radio transcripts from NASA missions, pairing them with great graphic design, and making the whole thing searchable and linkable. The result: A delightfully immersive perspective on history.", 
        "http://www.boingboing.net/2010/12/01/an-interactive-histo.html", "Boing Boing", "1 Dec, 2010",
    ),

    Thing(
        "If this isn’t making content meaningful, accessible (in a traditional sense), and enjoyable to consume, I don’t know what is.",
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
            'missions_coming_soon': missions_coming_soon
        },
        context_instance = RequestContext(request),
    )

def _get_amazon_url(country_code, asin):
    if country_code.lower() == 'uk':
        domain = 'co.uk'
        code = AFFILIATE_CODES['uk']
    else:
        domain = 'com'
        code = AFFILIATE_CODES['us']
    url = "http://www.amazon.%s/dp/%s" % (domain, asin)
    link_string = "http://www.amazon.%s/gp/redirect.html?ie=UTF8&location=%s&tag=%s" % \
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
    return render_to_response(
            'pages/about.html',
            {'READING_LISTS': _get_reading_list(request.META.get('GEOIP_COUNTRY_CODE', '--')), 'page': 'about'},
            context_instance = RequestContext(request),
            )

@cache_control(no_cache=True)
def press(request):
    return render_to_response(
            'pages/press.html',
            {
                'page': 'press',
                'NICE_THINGS': NICE_THINGS,
            },
            context_instance = RequestContext(request),
            )

@cache_control(no_cache=True)
def get_involved(request):
    return render_to_response(
            'pages/get-involved.html',
            {'READING_LISTS': _get_reading_list(request.META.get('GEOIP_COUNTRY_CODE', '--')), 'page': 'get-involved'},
            context_instance = RequestContext(request),
            )
