from public.message import query_currency_msg
from public.currency import Currency
from webpage.webClient import get_web_client
from webpage.comm.View import View
from django.shortcuts import render


class Inquiry(View):
    url = 'inquiry'

    def post(self, request):
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

    def get(self, request):
        return render(request, 'inquiry.html')
