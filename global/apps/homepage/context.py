from django.conf import settings

def static(request):
    return {
        "STATIC_URL": settings.STATIC_URL,
        "FIXED_STATIC_URL": settings.FIXED_STATIC_URL,
        "MISSIONS_STATIC_URL": settings.MISSIONS_STATIC_URL,
    }
