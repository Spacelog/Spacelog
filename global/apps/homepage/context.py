from django.conf import settings

def static(request):
    return {
        "STATIC_URL": settings.STATIC_URL,
    }
