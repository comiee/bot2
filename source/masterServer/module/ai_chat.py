from communication.asyncServer import AsyncServer
from public.log import master_server_logger
from public.config import get_config, data_path
from openai import AsyncOpenAI


async def get_ai_report(prompt, text):
    client = AsyncOpenAI(
        api_key=get_config('ai', 'api_key'),
        base_url="https://free.gpt.ge/v1/",
        default_headers={"x-foo": "true"},
    )
    completion = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt + '\n' + text,
            },
        ],
    )
    result = completion.choices[0].message.content
    master_server_logger.info(f'ai_chat 输入：{text}，输出：{result}')
    return result


@AsyncServer().register('ai_chat')
async def ai_chat(text):
    with open(data_path('prompt.txt'), encoding='utf-8') as f:
        prompt = f.read()
    result = await get_ai_report(prompt, text)
    master_server_logger.info(f'ai_chat 输入：{text}，输出：{result}')
    return result


@AsyncServer().register('ai_cat')
async def ai_cat(text):
    with open(data_path('prompt_cat.txt'), encoding='utf-8') as f:
        prompt = f.read()
    result = await get_ai_report(prompt, text)
    master_server_logger.info(f'ai_cat 输入：{text}，输出：{result}')
    return result
