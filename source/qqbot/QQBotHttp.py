from public.config import get_config
from public.log import qq_bot_logger
from public.exception import CustomException
import aiohttp
import time
from ssl import SSLContext
from typing import Literal


class QQBotHttp:
    def __init__(self, is_sandbox):
        self.__access_token = None
        self.__expires_in = 0
        self.__session = None
        self.__is_sandbox = is_sandbox


    async def _update_token(self):
        app_id = get_config('qqbot', 'appid')
        secret = get_config('qqbot', 'secret')
        async with aiohttp.ClientSession().post(
                url="https://bots.qq.com/app/getAppAccessToken",
                timeout=(aiohttp.ClientTimeout(total=20)),
                json={
                    "appId": app_id,
                    "clientSecret": secret,
                },
        ) as response:
            data = await response.json()
            if "access_token" not in data or "expires_in" not in data:
                raise CustomException(f"qqbot获取token失败，请检查appid和secret填写是否正确！data:{data}")
            qq_bot_logger.info(f'qqbot更新token：{data}')
            self.__access_token = data["access_token"]
            self.__expires_in = int(data["expires_in"]) + time.time()

    async def _get_token(self):
        if self.__access_token is None or time.time() >= self.__expires_in:
            await self._update_token()
        return self.__access_token

    async def _get_headers(self):
        return {
            "Authorization": f'QQBot {self._get_token()}',
            "X-Union-Appid": get_config('qqbot', 'appid'),
        }

    async def _get_session(self):
        if not self.__session or self.__session.closed:
            self.__session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=500, ssl=SSLContext(), force_close=True)
            )
        return self.__session

    def _get_url(self, path):
        if self.__is_sandbox:
            domain = "sandbox.api.sgroup.qq.com"
        else:
            domain = "api.sgroup.qq.com"

        return f'https://{domain}{path}'

    async def request(self, method:Literal['GET', 'POST'], path):
        session = await self._get_session()
        headers = await self._get_headers()
        url = self._get_url(path)
        qq_bot_logger.debug(f'qqbot请求头部：{headers}，请求方式：{method}，请求链接：{url}')

        try:
            async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=(aiohttp.ClientTimeout(total=5)),
            ) as response:
                condition = response.headers["content-type"] == "application/json"
                data = await response.json() if condition else await response.text()
                return data
        except Exception as e:
            qq_bot_logger.error(f'qqbot请求失败：{e.args[0]}')

    async def login(self):
        return await self.request('GET', "/users/@me")

    async def get_ws_url(self):
        return await self.request('GET', '/gateway/bot')