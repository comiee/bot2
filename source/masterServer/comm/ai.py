from public.config import get_config
from public.log import master_server_logger
from openai import AsyncOpenAI
from dataclasses import dataclass
import ollama
import asyncio
import re


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


@dataclass
class DeepSeekResult:
    content: str
    think: str
    result: str


async def get_deepseek_report(prompt, text) -> DeepSeekResult:
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
    content = response['message']['content'].replace('\n\n', '\n')
    master_server_logger.debug(f'prompt:\n{prompt}\ntext:\n{text}\ncontent:\n{content}')
    think, result = re.search(r'<think>\s*(.*)\s*</think>\s*(.*)', content, re.S).groups()
    return DeepSeekResult(content, think, result)


async def get_ai_report(prompt, text):
    try:
        return await get_gpt_report(prompt, text)
    except Exception as e:
        master_server_logger.error(f'调用ChatGPT api失败，将尝试使用本地deepseek回复。错误信息：{e}')
    try:
        deepseek_result = await get_deepseek_report(prompt, text)
        return deepseek_result.result
    except Exception as e:
        master_server_logger.error(f'调用本地deepseek失败，错误信息：{e}')
        return ''


def get_ai_report_sync(prompt, text):
    return asyncio.run(get_ai_report(prompt, text))
