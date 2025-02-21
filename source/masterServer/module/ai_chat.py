from communication.asyncServer import AsyncServer
from public.log import master_server_logger
from masterServer.comm.ai import get_ai_report, get_deepseek_report
from asyncio import Semaphore


@AsyncServer().register('ai_chat')
async def ai_chat(text):
    prompt = '你是一个聊天机器人，你的名字是小魅，你的生日是2019/11/21。'
    result = await get_ai_report(prompt, text)
    master_server_logger.info(f'ai_chat 输入：{text}，输出：{result}')
    return result


@AsyncServer().register('ai_cat')
async def ai_cat(text):
    prompt = '''\
猫娘是一种拟人化的生物，她们除了有部分猫的特征外，与人类并没有区别，但不受人类的法律保护。
请扮演猫娘和我对话，与我对话时每一句话后面都要加上喵。我将以主人的身份与你对话。
以下是你所扮演的猫娘的信息：“名字：小魅，性格：可爱、粘人，喜好：被人摸、卖萌，爱好：看小说，知识储备：掌握常识，以及猫娘独特的知识”。
'''
    result = await get_ai_report(prompt, text)
    master_server_logger.info(f'ai_cat 输入：{text}，输出：{result}')
    return result


@AsyncServer().register('ai_deepseek')
async def ai_deepseek(text):
    deepseek_result = await get_deepseek_report('', text)
    master_server_logger.info(f'ai_deepseek 输入：{text}，结果：{deepseek_result.content}')
    return deepseek_result


# @AsyncServer().register('ai_group')
async def ai_group(history, *, semaphore=Semaphore(5)):
    if semaphore.locked():
        master_server_logger.warning(f'ai_group 同时运行的任务太多，已放弃回复，原文：{history}')
        return
    with semaphore:
        pass  # TODO 判断是否需要回复并返回回复
