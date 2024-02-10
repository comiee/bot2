from public.message import momo_calendar_msg, query_currency_msg
from public.currency import Currency
from webpage.webClient import get_web_client
from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return render(request, 'index.html')


def momo_calendar(_):
    result = get_web_client().send(momo_calendar_msg.build())
    return HttpResponse(result)


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
