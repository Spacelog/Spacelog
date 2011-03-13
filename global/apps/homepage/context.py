from django.conf import settings

def static(request):
    return {
        "STATIC_URL": settings.STATIC_URL,
        "FIXED_STATIC_URL": settings.FIXED_STATIC_URL,
        "MISSIONS_STATIC_URL": settings.MISSIONS_STATIC_URL,
        "READING_LISTS": [
            [
                "By NASA astronauts and Soviet cosmonauts",
                [
                    [
                        "Deke!",
                        "Deke Slayton",
                        [
                            [ "http://amazon.com/", "Amazon US", ],
                            [ "http://amazon.co.uk/", "Amazon UK", ],
                        ],
                    ],
                    [
                        "We Seven",
                        "The Mercury Astronauts",
                        [
                            [ "http://amazon.com/", "Amazon US", ],
                            [ "http://amazon.co.uk/", "Amazon UK", ],
                        ],
                    ],
                    [
                        "We Have Capture",
                        "Tom Stafford",
                        [
                            [ "http://amazon.com/", "Amazon US", ],
                            [ "http://amazon.co.uk/", "Amazon UK", ],
                        ],
                    ],
                ],
            ],
            [
                "By other principals",
                [
                    [
                        "Flight",
                        "Chris Kraft",
                        [
                            [ "http://amazon.com/", "Amazon US", ],
                            [ "http://amazon.co.uk/", "Amazon UK", ],
                        ],
                    ],
                    [
                        "Mars Project",
                        "Werner von Braun",
                        [
                            [ "http://amazon.com/", "Amazon US", ],
                            [ "http://amazon.co.uk/", "Amazon UK", ],
                        ],
                    ],
                ],
            ],
            [
                "Other books",
                [
                    [
                        "Full Moon",
                        "",
                        [
                            [ "http://amazon.com/", "Amazon US", ],
                            [ "http://amazon.co.uk/", "Amazon UK", ],
                        ],
                    ],
                ],
            ],
        ],
    }
