from public.config import get_config
from openai import AsyncOpenAI
import asyncio


async def get_ai_report(prompt, text):
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


def get_ai_report_sync(prompt, text):
    return asyncio.run(get_ai_report(prompt, text))
