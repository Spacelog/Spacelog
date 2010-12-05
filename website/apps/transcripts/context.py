from django.conf import settings

def mission(request):
    return {
        "mission": getattr(request, 'mission', None),
        "PROJECT_HOME": settings.PROJECT_HOME,
    }

def static(request):
    return {
        "STATIC_URL": settings.STATIC_URL,
        "MISSIONS_STATIC_URL": settings.MISSIONS_STATIC_URL,
        "MISSIONS_PNG_URL": settings.MISSIONS_PNG_URL,
    }
