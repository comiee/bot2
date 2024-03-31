from public.message import web_login_msg
from public.error_code import ErrorCode
from webpage.webClient import get_web_client
from webpage.comm.View import View
from django.shortcuts import render
from django.http import HttpResponseRedirect


class Login(View):
    url = 'login'

    def post(self, request):
        if 'qq' not in request.session:
            return render(request, 'login.html', {'status': 0})
        qq = int(request.session['qq'])
        captcha = int(request.session.get('captcha', -1))
        ret = get_web_client().send(web_login_msg.build(
            user_id=qq,
            captcha=captcha,
        ))
        match ret:
            case ErrorCode.already_logged_in | ErrorCode.login_success:
                return HttpResponseRedirect('/index/')
            case ErrorCode.sent_captcha:
                return render(request, 'login.html', {'status': 1})
            case ErrorCode.wrong_captcha:
                return render(request, 'login.html', {'status': 2})
            case _:
                return render(request, 'login.html', {'status': 0})
