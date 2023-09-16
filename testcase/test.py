from masterServer import *
from masterServer.module.inquiry import query_currency

if __name__ == '__main__':
    load_module('module')
    server = get_master_server()
    Thread(target=server.run, daemon=True).start()
    print(query_currency(675110978, 'coin'))