from communication.asyncServer import AsyncServer
from public.log import master_server_logger
from public.config import get_config, data_path
from openai import AsyncOpenAI


@AsyncServer().register('ai_chat')
async def ai_chat(text):
    client = AsyncOpenAI(
        api_key=get_config('ai', 'api_key'),
        base_url="https://free.gpt.ge/v1/",
        default_headers={"x-foo": "true"},
    )
    with open(data_path('prompt.txt'), encoding='utf-8') as f:
        prompt = f.read()
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