from public.message import translate_msg
from public.log import master_server_logger
from public.config import get_config
import requests
import random
from hashlib import md5


def _map_language(name):
    language_map = {
        '自动检测': 'auto',
        '中': 'zh',
        '汉': 'zh',
        '英': 'en',
        '粤': 'yue',
        '文言': 'wyw',
        '日': 'jp',
        '韩': 'kor',
        '法': 'fra',
        '西班牙': 'spa',
        '泰': 'th',
        '阿拉伯': 'ara',
        '俄': 'ru',
        '葡萄牙': 'pt',
        '德': 'de',
        '意大利': 'it',
        '希腊': 'el',
        '荷兰': 'nl',
        '波兰': 'pl',
        '保加利亚': 'bul',
        '爱沙尼亚': 'est',
        '丹麦': 'dan',
        '芬兰': 'fin',
        '捷克': 'cs',
        '罗马尼亚': 'rom',
        '斯洛文尼亚': 'slo',
        '瑞典': 'swe',
        '匈牙利': 'hu',
        '繁体中': 'cht',
        '越南': 'vie',
    }
    return language_map.get(name.strip('语文'), name)


@translate_msg.on_receive
def translate(from_, to_, text):
    from_ = _map_language(from_)
    to_ = _map_language(to_)

    app_key = get_config('translate', 'app_key')
    app_secret = get_config('translate', 'app_secret')

    salt = random.randint(32768, 65536)
    sign = app_key + text + str(salt) + app_secret
    md = md5()
    md.update(sign.encode('utf-8'))
    sign = md.hexdigest()

    url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        "appid": app_key,
        "q": text,
        "from": from_,
        "to": to_,
        "salt": salt,
        "sign": sign
    }
    resp = requests.post(url, params=data, headers=header)
    result = resp.json()
    if 'error_msg' in result:
        error_msg = result['error_msg']
        master_server_logger.warning(f'translate 出错：{error_msg}')
        return error_msg
    if 'trans_result' not in result or len(result['trans_result']) != 1 or 'dst' not in result['trans_result'][0]:
        master_server_logger.error(f'translate 解析爬取结果出错，结果为：{result}')
        return f'解析爬取结果出错，结果为：{result}'
    return result['trans_result'][0]['dst']
