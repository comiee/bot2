from public.message import sign_in_msg
from masterServer.comm.sql import sql


@sign_in_msg.on_receive
def sign(user_id):
    if not sql.check_connect():
        return 2
    if sql.execute(f'select * from info where qq={user_id} and date=curdate();'):
        return 1
    sql.execute(f'''
            insert into info(qq,coin,date,stamina) values({user_id},10,curdate(),200) 
            on duplicate key update coin=coin+10,date=curdate(),stamina=greatest(stamina,200);
        ''')
    return 0
