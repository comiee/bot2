from public.message import web_login_msg
from webpage.webClient import get_web_client
from webpage.comm.View import View
from django.shortcuts import render


class Login(View):
    url = 'login'

    def post(self, request):
        if 'qq' not in request.session:
            return render(request, 'index.html')
        ret = get_web_client().send(web_login_msg.build(
            user_id=int(request.session.get('qq',0)),
            verification=int(request.session.get('verification',0)),
        ))
