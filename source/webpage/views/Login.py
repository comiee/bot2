from public.message import web_login_msg
from public.error_code import ErrorCode
from webpage.webClient import get_web_client
from webpage.comm.View import View
from django.shortcuts import render
from django.http import HttpResponseRedirect


class Login(View):
    url = 'login'

    def post(self, request):
        if 'qq' not in request.POST or request.POST['qq'] == '':
            return render(request, 'login.html', {'status': 0})
        qq = int(request.POST['qq'])
        if request.POST['login']:
            captcha = int(request.POST.get('captcha',-1))
        else:
            captcha = -1
        ret = get_web_client().send(web_login_msg.build(
            user_id=qq,
            captcha=captcha,
        ))
        match ret:
            case ErrorCode.already_logged_in | ErrorCode.login_success:
                return HttpResponseRedirect('/index')
            case ErrorCode.sent_captcha:
                status = 1
            case ErrorCode.wrong_captcha:
                status = 2
            case _:
                status = 0
        return render(request, 'login.html', {
            'qq': qq,
            'status': status,
        })
