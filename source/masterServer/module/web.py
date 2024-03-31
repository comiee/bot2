from public.message import web_login_msg, send_qq_text_msg
from public.error_code import ErrorCode
from masterServer.masterServer import get_master_server
import random

INVALID_CAPTCHA = -1


class User:
    def __init__(self, user_id: int):
        self.__user_id = user_id
        self.__logged_in = False
        self.__captcha = random.randint(0, 9999)

    def is_logged_in(self):
        return self.__logged_in

    def send_captcha(self):
        get_master_server().send_to('bot', send_qq_text_msg.build(
            user_id=self.__user_id,
            text=f'您的验证码为{self.__captcha:04d}'
        ))

    def verify(self, captcha):
        if self.__captcha == captcha:
            self.__logged_in = True
        return self.__logged_in


user_dict: dict[int, User] = {}


@web_login_msg.on_receive
def web_login(user_id, captcha):
    if user_id not in user_dict:
        user_dict[user_id] = User(user_id)
    user = user_dict[user_id]
    if user.is_logged_in():
        return ErrorCode.already_logged_in
    if captcha == INVALID_CAPTCHA:
        user.send_captcha()
        return ErrorCode.sent_captcha
    if user.verify(captcha):
        return ErrorCode.login_success
    else:
        return ErrorCode.wrong_captcha
