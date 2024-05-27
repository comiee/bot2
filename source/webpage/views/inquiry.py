from public.message import query_currency_msg
from public.currency import Currency
from webpage.webClient import get_web_client
from webpage.mei.urls import register_url
from django.shortcuts import render


@register_url('inquiry')
def inquiry(request):
    if request.GET:
        return render(request, 'inquiry.html')
    result = ''
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
