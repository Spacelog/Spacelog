from django.conf import settings

def mission(request):
    return {
        "mission": getattr(request, 'mission', None),
        "PROJECT_HOME": settings.PROJECT_HOME,
        "MISSION_URL": "http://%s%s" % (
            request.META['HTTP_HOST'],
            # "apollo13.spacelog.org",
            '/',
        ),
    }

def static(request):
    return {
        "MISSIONS_IMAGE_URL": settings.MISSIONS_IMAGE_URL,
    }
