from public.message import query_currency_msg
from public.currency import Currency
from webpage.webClient import get_web_client
from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def inquiry(request):
    result = ''
    if request.POST:
        if qq := request.POST['qq']:
            coin = get_web_client().send(query_currency_msg.build(
                user_id=int(qq),
                currency=Currency.coin.name,
            ))
            result = f'金币：{coin}'
    return render(request, 'inquiry.html', {
        'result': result,
    })
