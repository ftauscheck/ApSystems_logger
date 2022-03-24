from class_ApSystems import ApSystems
import configparser
import mysql.connector

config = configparser.ConfigParser()
config.read('config.ini')
config_main = config['main']
config_database = config['database']

mydb = mysql.connector.connect(host=config_database["host"],
                               port=int(config_database["port"]),
                               user=config_database["user"],
                               passwd=config_database["pwd"])
cur_mysql = mydb.cursor(dictionary=True)

conexao = ApSystems(config_main["domain"], config_main["useragent"], config_main["username"], config_main["password"])
if conexao.is_logged():
    retorno = conexao.get_power(20220224)
    for linha in retorno['power']:
        sql_insert = 'INSERT INTO solar.power (time, ecu, power) VALUES (%s, %s, %s);'
        cur_mysql.execute(sql_insert, (retorno['power'][linha]['datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                                       retorno['ecu'],
                                       retorno['power'][linha]['power']))
    mydb.commit()

    ecu_id = {}
    cur_mysql.execute('select id, inverterInfoId from solar.panel;')
    for row in cur_mysql:
        ecu_id[row['inverterInfoId']] = row['id']

    for panel in retorno['ecu_power']:
        print('Panel: {}'.format(panel))
        for linha in retorno['ecu_power'][panel]:
            sql_insert = 'INSERT INTO solar.power_panel (time, power, panel) VALUES (%s, %s, %s);'
            cur_mysql.execute(sql_insert, (retorno['ecu_power'][panel][linha]['datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                                           retorno['ecu_power'][panel][linha]['power'],
                                           ecu_id[panel]))
    mydb.commit()
