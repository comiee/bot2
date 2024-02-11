from public.message import momo_calendar_msg, query_currency_msg
from public.currency import Currency
from webpage.webClient import get_web_client
from django.shortcuts import render
from django.http import HttpResponse
from urllib.parse import quote


def index(request):
    return render(request, 'index.html')


def momo_calendar(request):
    return render(request, 'momo_calendar.html')


def momo_calendar_download(_):
    result = get_web_client().send(momo_calendar_msg.build())
    filename = quote('美月もも直播日历.ics')
    return HttpResponse(result, content_type='text/plain', headers={
        'Content-Disposition': f'attachment; filename="{filename}"'
    })


def inquiry(request):
    qq = ''
    result = ''
    if request.POST:
        if qq := request.POST['qq']:
            coin = get_web_client().send(query_currency_msg.build(
                user_id=int(qq),
                currency=Currency.coin.name,
            ))
            result = f'金币：{coin}'
    return render(request, 'inquiry.html', {
        'qq': qq,
        'result': result,
    })
