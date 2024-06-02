from public.message import get_authority_message, set_authority_message
from public.error_code import ErrorCode
from masterServer.comm.sql_cmd import sql,has_column, get_authority, set_authority


@get_authority_message.on_receive
def _get_authority(user_id: int, user_type: str, auth_type: str) -> tuple[int, int]:
    if not sql.check_connect():
        return ErrorCode.sql_disconnected, 0
    if not has_column('authority', auth_type):
        return ErrorCode.sql_column_does_not_exist, 0
    level = get_authority(user_id, user_type, auth_type)
    return ErrorCode.success, level


@set_authority_message.on_receive
def _set_authority(user_id: int, user_type: str, auth_type: str, level: int) -> int:
    if not sql.check_connect():
        return ErrorCode.sql_disconnected
    if not has_column('authority', auth_type):
        return ErrorCode.sql_column_does_not_exist
    set_authority(user_id, user_type, auth_type, level)
    return ErrorCode.success
