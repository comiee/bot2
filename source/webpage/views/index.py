from public.message import query_currency_msg
from public.currency import Currency
from webpage.webClient import get_web_client
from webpage.mei.urls import register_url
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@register_url('')
@login_required
def index(request):
    qq = request.user.username
    coin = get_web_client().send(query_currency_msg.build(
        user_id=int(qq),
        currency=Currency.coin.name,
    ))
    return render(request, 'index.html', {
        'qq': qq,
        'coin': coin
    })
