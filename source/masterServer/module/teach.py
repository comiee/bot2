from public.message import teach_msg, forget_msg, diary_msg, show_answer_msg
from public.config import data_path, get_config
from public.error_code import ErrorCode
from public.log import master_server_logger
from masterServer.comm.sql_cmd import is_ban
import json
import re

chat_path = data_path('chat.txt')
teach_path = data_path('teach.json')
diary_path = data_path('diary.txt')


@teach_msg.on_receive
def teach(user_id: int, group_id: int, question: str, answer: str):
    if is_ban(user_id):
        return ErrorCode.black_list_user

    if not question.strip() or not answer.strip():
        return ErrorCode.empty_str

    with open(chat_path, encoding='utf-8') as f:
        for line in f.readlines():
            com = line.split('\t')[0]
            if '%%' not in com and re.search(com, question, re.S):
                return ErrorCode.conflict_with_template

    with open(teach_path, 'r', encoding='utf-8') as fin:
        data = json.load(fin)
        if answer in data.setdefault(question, []):
            return ErrorCode.already_learned

        data[question].append(answer)
        with open(teach_path, 'w', encoding='utf-8') as fout:
            json.dump(data, fout, ensure_ascii=False)
    with open(diary_path, 'a', encoding='utf-8') as fh:
        fh.write(repr(f'{group_id}@{user_id}:{question}#{answer}') + '\n')
    master_server_logger.info(f'用户{group_id}@{user_id}进行调教：{question}#{answer}')
    return ErrorCode.success


@forget_msg.on_receive
def forget(user_id: int, group_id: int, question: str, answer: str):
    if is_ban(user_id):
        return ErrorCode.black_list_user

    with open(teach_path, encoding='utf-8') as fin:
        data = json.load(fin)
        if question not in data:
            return ErrorCode.not_remember
        if not answer:
            if user_id in get_config('admin', 'super_user'):
                del data[question]
            else:
                return ErrorCode.not_super_user
        else:
            if answer not in data[question]:
                return ErrorCode.not_remember
            data[question].remove(answer)
            if not data[question]:
                del data[question]
        with open(teach_path, 'w', encoding='utf-8') as fout:
            json.dump(data, fout, ensure_ascii=False)
        master_server_logger.info(f'用户{group_id}@{user_id}进行洗脑：{question}#{answer}')
        return ErrorCode.success


@diary_msg.on_receive
def diary(start: int, end: int):
    with open(diary_path, 'r', encoding='utf-8') as fh:
        history = [eval(i.strip()) for i in fh.readlines()]
        return history[start:end + 1]


@show_answer_msg.on_receive
def show_answer(question: str):
    with open(teach_path, encoding='utf-8') as f:
        data = json.load(f)
        return data.get(question, [])
