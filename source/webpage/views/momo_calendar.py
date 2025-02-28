from webpage.mei.urls import register_url
from public.message import momo_calendar_msg
from webpage.webClient import get_web_client
from django.shortcuts import render
from django.http import HttpResponse
from urllib.parse import quote


@register_url('momo_calendar')
def momo_calendar(request):
    if 'download' in request.GET:
        result = get_web_client().send(momo_calendar_msg.build())
        filename = quote('美月もも直播日历.ics')
        return HttpResponse(result, content_type='text/plain', headers={
            'Content-Disposition': f'attachment; filename="{filename}"'
        })
    else:
        return render(request, 'momo_calendar.html')
