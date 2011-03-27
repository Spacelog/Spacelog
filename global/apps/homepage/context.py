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
                        "Deke Slayton with Michael Cassutt",
                        [
                            [ "http://www.amazon.com/Deke-Autobiography-Donald-K-Slayton/dp/031285918X", "Amazon US", ],
                            [ "http://www.amazon.co.uk/Deke-Autobiography-Donald-K-Slayton/dp/031285918X", "Amazon UK", ],
                        ],
                    ],
                    [
                        "We Seven",
                        "The Mercury Astronauts",
                        [
                            [ "http://www.amazon.com/Seven-Astronauts-Themselves-Scott-Carpenter/dp/1439181039", "Amazon US", ],
                            [ "http://www.amazon.co.uk/Seven-Astronauts-Themselves-Scott-Carpenter/dp/1439181039", "Amazon UK", ],
                        ],
                    ],
                    [
                        "We Have Capture",
                        "Tom Stafford with Michael Cassutt",
                        [
                            [ "http://www.amazon.com/We-Have-Capture-Stafford-Space/dp/1588341011/", "Amazon US", ],
                            [ "http://www.amazon.co.uk/We-Have-Capture-Stafford-Space/dp/1588341011/", "Amazon UK", ],
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
                            [ "http://www.amazon.com/Flight-My-Life-Mission-Control/dp/B000EXYZR2/", "Amazon US", ],
                            [ "http://www.amazon.co.uk/Flight-My-Life-Mission-Control/dp/B000EXYZR2/", "Amazon UK", ],
                        ],
                    ],
                    [
                        "Project Mars: A Technical Tale",
                        "Werner von Braun",
                        [
                            [ "http://www.amazon.com/Project-Mars-Wernher-Von-Braun/dp/0973820330/", "Amazon US", ],
                            [ "http://www.amazon.co.uk/Project-Mars-Wernher-Von-Braun/dp/0973820330/", "Amazon UK", ],
                        ],
                    ],
                ],
            ],
            [
                "Other books",
                [
                    [
                        "Full Moon",
                        "Michael Light",
                        [
                            [ "http://www.amazon.com/Full-Moon-Andrew-Chaikin/dp/0375406344/", "Amazon US", ],
                            [ "http://www.amazon.co.uk/Full-Moon-Andrew-Chaikin/dp/0375406344/", "Amazon UK", ],
                        ],
                    ],
                ],
            ],
        ],
    }
