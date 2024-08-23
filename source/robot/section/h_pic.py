from communication.asyncClient import AsyncClient
from public.log import bot_logger
from public.currency import Currency
from public.tools import to_int
from robot.comm.pluginBase import Session
from robot.comm.command import KeywordCommand, FullCommand, RegexCommand
from alicebot.adapter.mirai.message import MiraiMessageSegment
import traceback

# TODO 白名单的判断放到服务端，使用权限控制数据库
white_groups = {694541980, 811912656, 324085758, 272943085}
white_friends = {1440667228, 2667336028, 1192916519, 2856606631}


@FullCommand('色图帮助').trim_white_list(groups=white_groups, friends=white_friends)
async def h_pic_help(session: Session):
    await session.reply('''\
参数使用方法举例：
色图 数量=1 等级=2
支持以下参数：
数量：1~20，默认为1
等级：0为非R18，1为不区分是否R18，2为全R18，默认为1，每个等级的色图价格不同，分别为：等级0每张10金币；等级1每张20金币，等级2每张30金币
关键字：按关键字模糊搜索，使用此功能会加收10金币
标签：匹配标签、作者名、标题，可用|指定“或”规则（最多20个），用&指定“且”规则（最多3个），例：萝莉|少女&白丝|黑丝 会查找(萝莉或少女)的(白丝或黑丝)色图，使用此功能会加收10金币
作者：指定作者的uid，可指定多个，用逗号隔开，最多可指定20个，使用此功能会加收10金币
排除AI：1为排除，0为不排除，默认为1
''')


# noinspection PyPep8Naming
async def get_h_pic(
        r18: int = None,
        num: int = None,
        uid: list[int] = None,
        keyword: str = None,
        tag: list[str] = None,
        size: list[str] = None,
        proxy: str = None,
        dateAfter: int = None,
        dateBefore: int = None,
        dsc: bool = None,
        excludeAI: bool = None
):
    post_json = {
        'r18': r18,
        'num': num,
        'uid': uid,
        'keyword': keyword,
        'tag': tag,
        'size': size,
        'proxy': proxy,
        'dateAfter': dateAfter,
        'dateBefore': dateBefore,
        'dsc': dsc,
        'excludeAI': excludeAI,
    }
    post_json = {k: v for k, v in post_json.items() if v is not None}
    async with AsyncClient('h_pic') as client:
        res = await client.send(post_json)
        return res


# noinspection NonAsciiCharacters,PyPep8Naming
@KeywordCommand('色图').trim_white_list(groups=white_groups, friends=white_friends)
async def h_pic(session: Session,
                数量: str = '1',
                等级: str = '1',
                关键字: str = None,
                标签: str = None,
                作者: str = None,
                排除AI: str = '1'
                ):
    try:
        num = int(数量)
        assert 1 <= num <= 20
        level = int(等级)
        assert 0 <= level <= 2
        keyword = 关键字
        tag = 标签 and 标签.split('&')
        uid = 作者 and list(map(int, 作者.split(',，')))
        no_AI = int(排除AI)
        assert 0 <= no_AI <= 1
        excludeAI = bool(no_AI)
    except:
        bot_logger.warning(f'h_pic 参数错误：{traceback.format_exc()}')
        await session.reply('参数错误，请检查参数，获取参数使用方法请使用命令：色图帮助')
        return
    r18 = {0: 0, 1: 2, 2: 1}[level]
    unit_price = 10 + 10 * (level + bool(keyword) + bool(tag) + bool(uid))
    max_price = unit_price * num
    await session.check_cost((max_price, Currency.coin))

    res = await get_h_pic(r18, num, uid, keyword, tag, excludeAI=excludeAI)
    if 'error' in res:
        await session.reply(f'爬取失败，金币已返还：{res["error"]}')
        return
    data = res['data']
    count = len(data)
    coin = unit_price * count
    if count == 0:
        await session.reply('未找到符合条件的结果，金币已返还')
        return
    text = f'已找到{count}个结果'
    if count != num:
        text += f'，实际花费{coin}金币'
    text += '，结果如下：'
    for url in data:
        if r18:
            text += '\n' + url
        else:
            text += MiraiMessageSegment.image(url=url)
    await session.reply(text)
    await session.ensure_cost((coin, Currency.coin))


@RegexCommand(r'来([\d\-负〇一二三四五六七八九十百千万亿零壹贰叁肆伍陆柒捌玖拾佰仟億两貮兆]*)[张点](.*)色图') \
        .trim_white_list(groups=white_groups, friends=white_friends)
async def h_pic_regex(session: Session, num, keyword):
    num = to_int(num) if num else 1
    if num > 20:
        await session.reply('你要的太多了，小心樯橹灰飞烟灭哦')
        return
    elif num <= 0:
        await session.reply('不买就不要来打扰我，我可是很忙的')
        return
    await h_pic(session, 数量=num, 关键字=keyword)


@FullCommand('申请色图权限').trim_white_list(groups=white_groups, friends=white_friends)
async def h_pic_web_auth(session: Session):
    session.user.set_authority('h_pic', 1)
    await session.reply('权限自动审批完成')
