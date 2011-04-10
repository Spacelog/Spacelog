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
                            [ "http://www.amazon.com/gp/redirect.html?ie=UTF8&location=http%3A%2F%2Fwww.amazon.com%2FDeke-Autobiography-Donald-K-Slayton%2Fdp%2F031285918X&tag=spacelog-20", "Amazon US", ],
                            [ "http://www.amazon.co.uk/gp/redirect.html?ie=UTF8&location=http%3A%2F%2Fwww.amazon.co.uk%2FDeke-Autobiography-Donald-K-Slayton%2Fdp%2F031285918X&tag=spacelog-21", "Amazon UK", ],
                        ],
                    ],
                    [
                        "We Seven",
                        "The Mercury Astronauts",
                        [
                            [ "http://www.amazon.com/gp/redirect.html?ie=UTF8&location=http%3A%2F%2Fwww.amazon.com%2FSeven-Astronauts-Themselves-Scott-Carpenter%2Fdp%2F1439181039&tag=spacelog-20", "Amazon US", ],
                            [ "http://www.amazon.co.uk/gp/redirect.html?ie=UTF8&location=http%3A%2F%2Fwww.amazon.co.uk%2FSeven-Astronauts-Themselves-Scott-Carpenter%2Fdp%2F1439181039&tag=spacelog-21", "Amazon UK", ],
                        ],
                    ],
                    [
                        "We Have Capture",
                        "Tom Stafford with Michael Cassutt",
                        [
                            [ "http://www.amazon.com/gp/redirect.html?ie=UTF8&location=http%3A%2F%2Fwww.amazon.com%2FWe-Have-Capture-Stafford-Space%2Fdp%2F1588341011%2F&tag=spacelog-20", "Amazon US", ],
                            [ "http://www.amazon.co.uk/gp/redirect.html?ie=UTF8&location=http%3A%2F%2Fwww.amazon.co.uk%2FWe-Have-Capture-Stafford-Space%2Fdp%2F1588341011%2F&tag=spacelog-21", "Amazon UK", ],
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
                            [ "http://www.amazon.com/gp/redirect.html?ie=UTF8&location=http%3A%2F%2Fwww.amazon.com%2FFlight-My-Life-Mission-Control%2Fdp%2FB000EXYZR2%2F&tag=spacelog-20", "Amazon US", ],
                            [ "http://www.amazon.co.uk/gp/redirect.html?ie=UTF8&location=http%3A%2F%2Fwww.amazon.co.uk%2FFlight-My-Life-Mission-Control%2Fdp%2FB000EXYZR2%2F&tag=spacelog-21", "Amazon UK", ],
                        ],
                    ],
                    [
                        "Project Mars: A Technical Tale",
                        "Werner von Braun",
                        [
                            [ "http://www.amazon.com/gp/redirect.html?ie=UTF8&location=http%3A%2F%2Fwww.amazon.com%2FProject-Mars-Wernher-Von-Braun%2Fdp%2F0973820330%2F&tag=spacelog-20", "Amazon US", ],
                            [ "http://www.amazon.co.uk/gp/redirect.html?ie=UTF8&location=http%3A%2F%2Fwww.amazon.co.uk%2FProject-Mars-Wernher-Von-Braun%2Fdp%2F0973820330%2F&tag=spacelog-21", "Amazon UK", ],
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
                            [ "http://www.amazon.com/gp/redirect.html?ie=UTF8&location=http%3A%2F%2Fwww.amazon.com%2FFull-Moon-Andrew-Chaikin%2Fdp%2F0375406344%2F&tag=spacelog-20", "Amazon US", ],
                            [ "http://www.amazon.co.uk/gp/redirect.html?ie=UTF8&location=http%3A%2F%2Fwww.amazon.co.uk%2FFull-Moon-Andrew-Chaikin%2Fdp%2F0375406344%2F&tag=spacelog-21", "Amazon UK", ],
                        ],
                    ],
                ],
            ],
        ],
    }
