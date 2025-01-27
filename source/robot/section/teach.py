from public.message import teach_msg, forget_msg, diary_msg, show_answer_msg
from public.error_code import ErrorCode
from robot.comm.pluginBase import Session
from robot.comm.command import RegexCommand, ArgCommand, NormalCommand
from robot.botClient import get_bot_client


@RegexCommand(r'^调教 (.*?)#(.*)$')
async def teach(session: Session, question: str, answer: str):
    ret = get_bot_client().send(teach_msg.build(
        user_id=session.qq,
        group_id=session.id if session.is_group() else 0,
        question=question,
        answer=answer,
    ))
    match ret:
        case ErrorCode.success:
            await session.reply('小魅记住了！')
        case ErrorCode.empty_str:
            await session.reply('问题或回答为空！')
        case ErrorCode.conflict_with_template:
            await session.reply('调教词与原有模板冲突！')
        case ErrorCode.already_learned:
            await session.reply('小魅已经学会了这个回答了，不用再教了哦。')
        case _:
            await session.handle_error(ret)


@RegexCommand(r'^洗脑 (.*?)#(.*)$')
async def forget(session: Session, question: str, answer: str = ''):
    ret = get_bot_client().send(forget_msg.build(
        user_id=session.qq,
        group_id=session.id if session.is_group() else 0,
        question=question,
        answer=answer,
    ))
    match ret:
        case ErrorCode.success:
            await session.reply('唉？这个回答是不对的吗？好吧，小魅不会这么说了。')
        case ErrorCode.not_super_user:
            await session.reply('只有小魅的主人能使用批量洗脑功能哦。')
        case ErrorCode.not_remember:
            if answer:
                await session.reply('小魅并不记得这个回答哦。')
            else:
                await session.reply(f'小魅的大脑中并没有关于“{question}”的记忆哦。')
        case _:
            await session.handle_error(ret)


@ArgCommand('日记')
@ArgCommand('调教日记')
async def diary(session: Session, start: str = '0', end: str = '10'):
    try:
        start = int(start)
        end = int(end)
        assert 0 <= start < end
    except Exception:
        await session.reply('参数错误，命令已取消')
        return

    result = get_bot_client().send(diary_msg.build(
        start=start,
        end=end,
    ))
    if start == 0:
        await session.reply(f'近{end}次调教记录如下：\n' + '\n'.join(result))
    else:
        await session.reply(f'{start}~{end}次调教记录如下：\n' + '\n'.join(result))


@NormalCommand('显示 ')
async def show_answer(session: Session, question: str):
    result = get_bot_client().send(show_answer_msg.build(
        question=question,
    ))
    if result:
        await session.reply(repr(result))
    else:
        await session.reply(f'小魅的大脑中并没有关于“{question}”的记忆哦。')
