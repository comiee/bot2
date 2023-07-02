from communication import message


@message.chat_msg.on_receive
def chat(user_id, text):
    pass
