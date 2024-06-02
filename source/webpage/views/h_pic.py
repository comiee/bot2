from communication.asyncClient import AsyncClient
from public.message import query_currency_msg, get_authority_message
from public.log import web_logger
from public.error_code import ErrorCode
from public.currency import Currency
from webpage.webClient import get_web_client
from webpage.mei.urls import register_url
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import asyncio


def has_permission(qq: int) -> bool:
    ret, level = get_web_client().send(get_authority_message.build(
        user_id=qq,
        user_type='friend',
        auth_type='h_pic',
    ))
    return ret == ErrorCode.success and level > 0


# noinspection PyPep8Naming
async def get_h_pic(
        r18: int = None,
        uid: list[int] = None,
        keyword: str = None,
        tag: list[str] = None,
        excludeAI: bool = None
):
    post_json = {
        'r18': r18,
        'uid': uid,
        'keyword': keyword,
        'tag': tag,
        'excludeAI': excludeAI,
    }
    post_json = {k: v for k, v in post_json.items() if v is not None}
    async with AsyncClient('h_pic') as client:
        res = await client.send(post_json)
        return res


@register_url('h_pic')
@login_required
def h_pic(request):
    qq = int(request.user.username)

    coin = get_web_client().send(query_currency_msg.build(
        user_id=qq,
        currency=Currency.coin.name,
    ))
    return render(request, 'h_pic.html', {
        'qq': qq,
        'coin': coin,
        'has_permission': has_permission(qq),
    })


@register_url('generate_h_pic')
@login_required
def generate_h_pic(request):
    qq = int(request.user.username)

    if not has_permission(qq):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if request.method == 'POST':
        try:
            res = asyncio.run(get_h_pic(
                r18=request.POST.get('r18'),
                uid=request.POST.get('uid'),
                keyword=request.POST.get('keyword'),
                tag=request.POST.get('tag'),
                excludeAI=request.POST.get('excludeAI'),
            ))
            if 'error' in res:
                return JsonResponse({'fail': '爬取失败，金币已返还'})
            data = res['data']
            if len(data) == 0:
                return JsonResponse({'fail': '未找到符合条件的结果，金币已返还'})
            image_url = data[0]
            return JsonResponse({'image_url': image_url})
        except Exception as e:
            web_logger.exception(f'h_pic爬取图片失败：{e}')
            return JsonResponse({'fail': '爬取出错，请联系小魅的主人'})

    return JsonResponse({'error': 'Invalid request'}, status=400)
