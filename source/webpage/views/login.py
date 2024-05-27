from public.message import send_qq_text_msg
from webpage.webClient import get_web_client
from webpage.mei.urls import register_url
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import random

verification_code = {}


@register_url('login')
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        qq = request.POST.get('qq')
        code = request.POST.get('code')
        if qq in verification_code and verification_code[qq] == code:
            # 登录用户
            user = authenticate(request, username=qq, code=code)
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': '登录失败'})
        else:
            return JsonResponse({'success': False, 'error': '验证码错误'})
    return render(request, 'login.html')


@register_url('send_verification')
@require_POST
@csrf_exempt
def send_verification_view(request):
    qq = request.POST.get('qq')
    if qq:
        code = str(random.randint(1000, 9999))
        verification_code[qq] = code
        ret = get_web_client().send(send_qq_text_msg.build(
            user_id=int(qq),
            text=f'您的验证码为：{code}',
        ))
        if ret:
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': '发送验证码失败，请检查小魅是否为您的好友'})
    return JsonResponse({'success': False, 'error': 'QQ号为空'})


@register_url('logout')
@login_required
def logout_view(request):
    qq = request.user.username
    if qq in verification_code:
        del verification_code[qq]
    logout(request)
    return redirect('login')
