from public.config import get_config
from public.log import master_server_logger
from openai import AsyncOpenAI
import ollama
import asyncio


async def get_gpt_report(prompt, text):
    # api使用方法见 https://github.com/chatanywhere/GPT_API_free
    client = AsyncOpenAI(
        api_key=get_config('ai', 'api_key'),
        base_url="https://api.chatanywhere.tech/v1",
        default_headers={"x-foo": "true"},
    )
    completion = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": text,
            },
        ],
    )
    result = completion.choices[0].message.content
    return result


async def get_local_report(prompt, text):
    response = await ollama.AsyncClient().chat(
        model="deepseek-r1:1.5b",
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": text,
            },
        ],
    )
    content = response['message']['content']
    master_server_logger.debug(f'prompt:\n{prompt}\ntext:\n{text}\ncontent:\n{content}')
    result = content.split('</think>')[-1].lstrip('\n')
    return result


async def get_ai_report(prompt, text):
    # try:
    #     return await get_local_report(prompt, text)
    # except Exception as e:
    #     master_server_logger.error(f'调用本地ai失败，将使用ChatGPT回复。错误信息：{e}')
    #     return await get_gpt_report(prompt, text)
    return await get_gpt_report(prompt, text)


def get_ai_report_sync(prompt, text):
    return asyncio.run(get_ai_report(prompt, text))
