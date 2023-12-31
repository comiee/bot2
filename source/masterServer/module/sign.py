from public.message import sign_in_msg
from public.error_code import ErrorCode
from masterServer.comm.sql import sql


@sign_in_msg.on_receive
def sign(user_id):
    if not sql.check_connect():
        return ErrorCode.sql_disconnected
    if sql.execute(f'select * from info where qq={user_id} and date=curdate();'):
        return ErrorCode.already_signed
    sql.execute(f'''
            insert into info(qq,coin,date,stamina) values({user_id},10,curdate(),200) 
            on duplicate key update coin=coin+10,date=curdate(),stamina=greatest(stamina,200);
        ''')
    return ErrorCode.success
