from django.conf import settings

def mission(request):
    return {
        "mission": request.mission,
        "PROJECT_HOME": settings.PROJECT_HOME,
    }
