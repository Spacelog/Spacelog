from django.shortcuts import render_to_response

def people(request):
    return render_to_response(
        'people/people.html',
        {},
    )