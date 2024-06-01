from communication.asyncServer import AsyncServer
import aiohttp


@AsyncServer().register('baike')
async def baike(question):
    try:
        async with aiohttp.ClientSession() as clientSession:
            url = f'https://baike.deno.dev/item/{question}?encoding=text'
            async with clientSession.get(url) as resp:
                return await resp.text('utf-8')
    except Exception as e:
        return str(e)
