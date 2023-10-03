from public.message import translate_msg
from robot.botClient import get_bot_client
from robot.comm.pluginBase import Session
from robot.comm.command import NormalCommand, RegexCommand


def translate(from_: str, to_: str, text: str) -> str:
    return get_bot_client().send(translate_msg.build({
        'from_': from_,
        'to_': to_,
        'text': text,
    }))


@RegexCommand(r'(.*?)[语文]?译(.*?)[语文]? (.*)')
async def translate_from_to(session: Session, from_: str, to_: str, text: str) -> None:
    result = translate(from_, to_, text)
    await session.reply(result)


@RegexCommand(r'(.*)用(.*?)[语文]?怎么说')
async def translate_to(session: Session, text: str, to_: str) -> None:
    result = translate('auto', to_, text)
    await session.reply(result)


@NormalCommand('翻译')
@RegexCommand(r'(.*)是什么意思')
async def translate_auto(session: Session, text: str) -> None:
    result = translate('auto', 'zh', text)
    if result == text:
        result = translate('auto', 'en', text)
    await session.reply(result)
