"""消息格式转换"""
from public.log import public_logger
from alicebot.message import BuildMessageType
from alicebot.adapter.mirai.message import MiraiMessage, MiraiMessageSegment
from typing import Literal
import re

"""
internal格式：
[类型:主要值,键:其他值...]
类型使用小驼峰命名
原文的[]用[left]和[right]表示
"""


def convert_mirai_to_data(message: BuildMessageType) -> list[dict]:
    return MiraiMessage(message).as_message_chain()


def convert_data_to_mirai(data: list[dict]) -> MiraiMessage:
    return MiraiMessage([MiraiMessageSegment(**x) for x in data])


def convert_internal_part_to_mirai_seg(s: str) -> MiraiMessageSegment:
    pairs = [x.split(':', 1) for x in s.split(',')]
    temp = eval('dict(pairs)')
    type_, value = pairs[0][0], pairs[0][1]
    match type_:
        case 'at':
            return MiraiMessageSegment.at(int(value))
        case 'atAll':
            return MiraiMessageSegment.at_all()
        case 'face':
            return MiraiMessageSegment.face(int(value))
        case 'image':
            return MiraiMessageSegment.image(
                image_id=value,
                url=temp['url'],
            )
        case 'flashImage':
            return MiraiMessageSegment.flash_image(value)
        case 'voice':
            return MiraiMessageSegment.voice(value)
        case 'xml':
            return MiraiMessageSegment.xml(value)
        case 'json':
            return MiraiMessageSegment.json(value)
        case 'app':
            return MiraiMessageSegment.app(value)
        case 'poke':
            return MiraiMessageSegment.poke(value)
        case 'dice':
            return MiraiMessageSegment.dice(int(value))
        case 'musicShare':
            return MiraiMessageSegment.music_share(
                kind=temp['kind'],
                title=temp['title'],
                summary=temp['summary'],
                jump_url=temp['jump_url'],
                picture_url=temp['picture_url'],
                music_url=temp['music_url'],
                brief=temp['brief'],
            )
        case 'file':
            return MiraiMessageSegment('File', name=value)
        case 'marketFace':
            return MiraiMessageSegment('MarketFace', id=value)
        case _:
            return MiraiMessageSegment.plain(value)


def convert_internal_to_mirai(msg: str) -> MiraiMessage:
    stack = []
    for c in msg:
        match c:
            case '[':
                stack.append('')
            case ']':
                if stack[-1] == 'left' or stack[-1] == 'right':
                    k = stack.pop()
                    if not stack:
                        stack.append('')
                    v = {'left': '[', 'right': ']'}[k]
                    if isinstance(stack[-1], str):
                        stack[-1] += v
                    else:
                        stack.append(v)
                else:
                    stack[-1] = convert_internal_part_to_mirai_seg(stack[-1])
            case _:
                if not stack:
                    stack.append('')
                if isinstance(stack[-1], str):
                    stack[-1] += c
                else:
                    stack.append(c)
    return MiraiMessage([MiraiMessageSegment.plain(x) if isinstance(x, str) else x for x in stack])


def convert_internal_to_data(msg: str) -> list[dict]:
    return convert_internal_to_mirai(msg).as_message_chain()


def convert_dict_to_internal(d: dict) -> str:
    def g(k):
        return d.get(k, '')

    match d["type"]:
        case 'Source' | 'Quote':
            return ''
        case 'At':
            return f'[at:{g("target")}]'
        case 'AtAll':
            return f'[atAll:]'
        case 'Face':
            return f'[face:{g("faceId")}]'
        case 'Image':
            return f'[image:{g("imageId")},url:{g("url")}]'
        case 'FlashImage':
            return f'[flashImage:{g("imageId")}]'
        case 'Voice':
            return f'[voice:{g("imageId")}]'
        case 'Xml':
            return f'[xml:{g("xml")}]'
        case 'Json':
            return f'[json:{g("json")}]'
        case 'App':
            return f'[app:{g("content")}]'
        case 'Poke':
            return f'[poke:{g("name")}]'
        case 'Dice':
            return f'[dice:{g("value")}]'
        case 'MusicShare':
            return f'[musicShare:{g("title")},kind:{g("kind")},title:{g("title")},summary:{g("summary")},' \
                   f'jumpUrl:{g("jumpUrl")},pictureUrl:{g("pictureUrl")},musicUrl:{g("musicUrl")},brief:{g("brief")}]'
        case 'File':
            return f'[file:{g("name")}]'
        case 'MarketFace':
            return f'[marketFace:{g("id")}]'
        case 'Plain':
            return re.sub(r'[\[\]]', lambda m: {'[': '[left]', ']': '[right]'}[m.group()], g("text"))
        case _:
            public_logger.error(f'未知的类型的消息：{d}')
            s = ','.join(f'{k}:{v}' for k, v in d.items() if k != 'type')
            return f'[unknown:{g("type")},{s}]'


def convert_data_to_internal(data: list[dict]) -> str:
    return ''.join(map(convert_dict_to_internal, data))


def convert_mirai_to_plain(message: BuildMessageType) -> str:
    return MiraiMessage(message).get_plain_text()


def convert_plain_to_mirai(text: str) -> MiraiMessage:
    return MiraiMessage(MiraiMessageSegment.plain(text))


MsgType = Literal['internal', 'mirai', 'data', 'plain']


def convert(type_a: MsgType, type_b: MsgType, msg):
    # 直接转换
    fun_name = f'convert_{type_a}_to_{type_b}'
    if fun_name in globals():
        return globals()[fun_name](msg)
    # 通过data格式转换
    fun_name_a = f'convert_{type_a}_to_data'
    fun_name_b = f'convert_data_to_{type_b}'
    if fun_name_a in globals() and fun_name_b in globals():
        temp = globals()[fun_name_a](msg)
        return globals()[fun_name_b](temp)
    # 通过mirai格式转换
    fun_name_a = f'convert_{type_a}_to_mirai'
    fun_name_b = f'convert_mirai_to_{type_b}'
    if fun_name_a in globals() and fun_name_b in globals():
        temp = globals()[fun_name_a](msg)
        return globals()[fun_name_b](temp)
    raise Exception(f'找不到将{type_a}转换为{type_b}的函数')


def convert_to(type_b: MsgType, msg):
    if isinstance(msg, str):
        type_a: MsgType = 'internal'
    elif isinstance(msg, (MiraiMessage, MiraiMessageSegment)):
        type_a: MsgType = 'mirai'
    elif isinstance(msg, dict):
        type_a: MsgType = 'data'
    else:
        raise Exception(f'无法解析的msg类型{type(msg)}')
    return convert(type_a, type_b, msg)
