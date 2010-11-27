from django.shortcuts import render_to_response
from django.template import RequestContext
from backend.api import Glossary


def glossary(request):
    terms = sorted(
        list(
            Glossary.Query(request.redis_conn, request.mission.name).items()
        ),
        key=lambda term: term.abbr,
    )
    
    return render_to_response(
        'glossary/glossary.html',
        {
            'terms': terms,
        },
        context_instance = RequestContext(request),
    )
