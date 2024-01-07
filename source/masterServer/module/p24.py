from public.message import p24_start_msg, p24_game_msg, p24_over_msg
from public.error_code import ErrorCode
from public.currency import Currency
from masterServer.comm.sql_cmd import sql, increase_currency
import re
import random
from collections import defaultdict


class P24Game:
    # 穷举无法计算的题目
    __BAD_QUESTIONS = {(1, 1, 1, 1), (1, 1, 1, 2), (1, 1, 1, 3), (1, 1, 1, 4), (1, 1, 1, 5), (1, 1, 1, 6), (1, 1, 1, 7),
                       (1, 1, 1, 9), (1, 1, 2, 2), (1, 1, 2, 3), (1, 1, 2, 4), (1, 1, 2, 5), (1, 1, 3, 3), (1, 1, 5, 9),
                       (1, 1, 6, 7), (1, 1, 7, 7), (1, 1, 7, 8), (1, 1, 7, 9), (1, 1, 8, 9), (1, 1, 9, 9), (1, 2, 2, 2),
                       (1, 2, 2, 3), (1, 2, 9, 9), (1, 3, 5, 5), (1, 4, 9, 9), (1, 5, 5, 7), (1, 5, 5, 8), (1, 5, 7, 7),
                       (1, 6, 6, 7), (1, 6, 7, 7), (1, 6, 7, 8), (1, 7, 7, 7), (1, 7, 7, 8), (1, 8, 9, 9), (1, 9, 9, 9),
                       (2, 2, 2, 2), (2, 2, 2, 6), (2, 2, 7, 9), (2, 2, 9, 9), (2, 3, 3, 4), (2, 5, 5, 5), (2, 5, 5, 6),
                       (2, 5, 9, 9), (2, 6, 7, 7), (2, 7, 7, 7), (2, 7, 7, 9), (2, 7, 9, 9), (2, 9, 9, 9), (3, 3, 5, 8),
                       (3, 4, 6, 7), (3, 4, 8, 8), (3, 5, 5, 5), (3, 5, 7, 7), (4, 4, 5, 9), (4, 4, 6, 6), (4, 4, 6, 7),
                       (4, 4, 9, 9), (4, 7, 7, 9), (4, 9, 9, 9), (5, 5, 5, 7), (5, 5, 5, 8), (5, 5, 6, 9), (5, 5, 7, 9),
                       (5, 7, 7, 7), (5, 7, 7, 8), (5, 7, 9, 9), (5, 8, 9, 9), (5, 9, 9, 9), (6, 6, 6, 7), (6, 6, 7, 7),
                       (6, 6, 7, 8), (6, 6, 9, 9), (6, 7, 7, 7), (6, 7, 7, 8), (6, 7, 7, 9), (6, 7, 8, 8), (6, 9, 9, 9),
                       (7, 7, 7, 7), (7, 7, 7, 8), (7, 7, 7, 9), (7, 7, 8, 8), (7, 7, 8, 9), (7, 7, 9, 9), (7, 8, 8, 8),
                       (7, 8, 9, 9), (7, 9, 9, 9), (8, 8, 8, 8), (8, 8, 8, 9), (8, 8, 9, 9), (8, 9, 9, 9), (9, 9, 9, 9)}

    __instances: dict[int, 'P24Game'] = {}

    def __init__(self, group_id: int):
        self.__group_id = group_id
        self.game_start()

    def __set_question(self):
        """出题"""
        while 1:
            q = random.choices(range(1, 10), k=4)
            if tuple(sorted(q)) not in self.__BAD_QUESTIONS:
                self.__question = q
                return

    def game_start(self):
        self.__score: dict[int, int] = defaultdict(int)
        self.__set_question()

        P24Game.__instances[self.__group_id] = self
        return self.__question

    def game_run(self, user_id: int, answer: str) -> tuple[int, list]:
        if not sql.check_connect():
            return ErrorCode.sql_disconnected, self.__question
        if not re.search(r'^[\d+\-*/^()（）]+$', answer):  # 判断是否是式子
            return ErrorCode.not_equation, self.__question

        nums = [int(i) for i in re.findall(r'\d+', answer)]
        if sorted(self.__question) != sorted(nums):  # 判断使用的数
            return ErrorCode.not_compliant_rule, self.__question
        if round(eval(answer.replace('^', '**').replace('（', '(').replace('）', ')')), 10) == 24:  # 判断式子的结果
            self.__score[user_id] += 5
            increase_currency(user_id, Currency.coin, 5)
            self.__set_question()
            self.__count = 0
            return ErrorCode.correct_answer, self.__question
        else:
            return ErrorCode.wrong_answer, self.__question

    def game_over(self) -> list[tuple[int, int]]:
        del P24Game.__instances[self.__group_id]
        return list(self.__score.items())

    @classmethod
    def get_instance(cls, group_id: int):
        if group_id not in cls.__instances:
            P24Game(group_id).game_start()
        return cls.__instances[group_id]


@p24_start_msg.on_receive
def p24_start(group_id: int) -> list:
    return P24Game.get_instance(group_id).game_start()


@p24_game_msg.on_receive
def p24_game(group_id: int, user_id: int, answer: str) -> tuple[int, list]:
    return P24Game.get_instance(group_id).game_run(user_id, answer)


@p24_over_msg.on_receive
def p24_over(group_id: int) -> list[tuple[int, int]]:
    return P24Game.get_instance(group_id).game_over()

# TODO 客户端断连自动结束游戏
