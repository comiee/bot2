from public.message import web_login_msg

INVALID_VERIFICATION = -1


class User:
    def __init__(self, user_id: int):
        self.__user_id = user_id
        self.__logged_in = False
        self.__verification = INVALID_VERIFICATION

    def is_logged_in(self):
        return self.__logged_in

    def verify(self, verification):
        if self.__verification == verification:
            self.__logged_in = True
        return self.__logged_in


user_dict: dict[int, User] = {}


@web_login_msg.on_receive
def web_login(user_id, verification):
    if user_id not in user_dict:
        user_dict[user_id] = User(user_id)
    user = user_dict[user_id]
    if user.is_logged_in():
        return 0  # todo 换成登录成功错误码
    # todo 发送验证码等处理
