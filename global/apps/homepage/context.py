from django.conf import settings

def static(request):
    return {
        "STATIC_URL": settings.STATIC_URL,
        "MISSIONS_STATIC_URL": settings.MISSIONS_STATIC_URL,
    }
