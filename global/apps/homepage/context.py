from django.conf import settings

def static(request):
    return {
        "MISSIONS_STATIC_URL": settings.MISSIONS_STATIC_URL,
    }
