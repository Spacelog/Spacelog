from django.shortcuts import render_to_response
import redis
from backend.api import Glossary


def glossary(request):
    redis_conn = redis.Redis()
    terms      = list( Glossary.Query( redis_conn, 'a13' ).items() )
    
    return render_to_response(
        'glossary/glossary.html',
        {
            'terms': terms,
        }
    )
