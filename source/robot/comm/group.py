from public.message import *
from robot.botClient import get_bot_client


class Group(int):
    def get_authority(self, auth_type: str) -> int:
        return get_bot_client().send(get_authority_message.build(
            user_id=int(self),
            user_type='group',
            auth_type=auth_type,
        ))

    def set_authority(self, auth_type: str, level: int) -> bool:
        return get_bot_client().send(set_authority_message.build(
            user_id=int(self),
            user_type='group',
            auth_type=auth_type,
            level=level,
        ))
